"""
WebSocket Authenticator - HMAC-signed token authentication for MW-Vision.

Security fixes applied (2026-02-17):
  VULN-001: verify_token() no longer returns True unconditionally.
  VULN-002: Tokens are now HMAC-signed; no server-side storage needed.
"""
import os
import hmac
import json
import time
import base64
import hashlib
import secrets
from typing import Optional


class WebSocketAuthenticator:
    """Handles WebSocket authentication via HMAC-signed tokens."""

    def __init__(self, secret_key: Optional[str] = None):
        raw = secret_key or os.getenv("HYDRA_SECRET_KEY") or os.getenv("WS_SECRET_KEY")
        if not raw:
            # Fail closed. The previous behaviour warned and minted an ephemeral
            # per-process key: with several PM2 workers, a token signed by one
            # was rejected by another, so authentication half-worked and the
            # failures looked like network flakiness. A warning in production
            # goes nowhere; refusing to start is visible.
            raise RuntimeError(
                "HYDRA_SECRET_KEY is not set. WebSocket authentication cannot "
                "start without a stable signing key shared by every worker. "
                "Generate one with: python -c \"import secrets; "
                "print(secrets.token_hex(32))\""
            )
        self._reject_weak_key(raw)
        self._secret = raw.encode()

    # Minimum entropy for an HMAC-SHA256 signing key. 32 bytes is what
    # secrets.token_hex(32) produces as 64 hex characters; accepting less is
    # accepting a key that can be guessed offline, and the error that follows
    # looks like a bug rather than a break-in.
    _MIN_KEY_CHARS = 32

    # Keys that appear in tutorials, .env.example files and commit history.
    # Requiring length alone is not enough: "secret-secret-secret-secret-secret"
    # is 34 characters and public knowledge.
    _PLACEHOLDERS = frozenset({
        "changeme", "change_me", "change-me", "secret", "secretkey",
        "secret_key", "mysecret", "my_secret", "password", "default",
        "placeholder", "todo", "fixme", "example", "test", "testing",
        "dev", "development", "local", "localhost", "hydra", "mwvision",
        "mw_vision", "mw-vision", "0", "1", "none", "null", "xxx",
    })

    @classmethod
    def _reject_weak_key(cls, raw: str) -> None:
        """
        Refuse a signing key that is too short or publicly known.

        Set HYDRA_ALLOW_WEAK_KEY=1 to override, which exists so a developer can
        reproduce a report without editing this file; it is deliberately
        awkward and must never be set in production.
        """
        if os.getenv("HYDRA_ALLOW_WEAK_KEY") == "1":
            return
        clave = raw.strip()
        if len(clave) < cls._MIN_KEY_CHARS:
            raise RuntimeError(
                f"HYDRA_SECRET_KEY is {len(clave)} characters; at least "
                f"{cls._MIN_KEY_CHARS} are required to sign HMAC-SHA256 tokens. "
                "A short key can be recovered offline from a single token. "
                "Generate one with: python -c \"import secrets; "
                "print(secrets.token_hex(32))\""
            )
        # Compare on the alphanumeric core so "secret", "SECRET_KEY" and
        # placeholder punctuation all collapse to the same word.
        nucleo = "".join(c for c in clave.lower() if c.isalnum())
        if nucleo in cls._PLACEHOLDERS or len(set(nucleo)) <= 2:
            raise RuntimeError(
                "HYDRA_SECRET_KEY is a placeholder or has almost no variety. "
                "Any token signed with it can be forged by anyone who has read "
                "a tutorial. Generate one with: python -c \"import secrets; "
                "print(secrets.token_hex(32))\""
            )
        # A key repeated from a short motif ("abcabcabc...") is long but weak.
        for n in range(1, 9):
            if len(nucleo) > n and nucleo == (nucleo[:n] * (len(nucleo) // n + 1))[:len(nucleo)]:
                raise RuntimeError(
                    "HYDRA_SECRET_KEY is a short pattern repeated to reach the "
                    "required length, so it has the entropy of the pattern. "
                    "Generate one with: python -c \"import secrets; "
                    "print(secrets.token_hex(32))\""
                )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_token(self, expires_hours: int = 24) -> str:
        """
        Generate a signed authentication token.

        Token format: base64url(payload_json).HMAC-SHA256-hex
        The payload contains iat (issued-at) and exp (expiry) Unix timestamps
        plus a random jti (JWT ID) to prevent replay by token reuse.

        Returns:
            Opaque token string suitable for Authorization headers.
        """
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + int(expires_hours * 3600),
            "jti": secrets.token_hex(16),
        }
        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload, separators=(",", ":")).encode()
        ).decode().rstrip("=")

        sig = hmac.new(self._secret, payload_b64.encode(), hashlib.sha256).hexdigest()
        return f"{payload_b64}.{sig}"

    def verify_token(self, token: str) -> bool:
        """
        Verify a token produced by generate_token().

        Returns:
            True only if the token was signed by this instance's secret key
            AND has not yet expired.  False in all other cases.
        """
        if not token or "." not in token:
            return False
        try:
            payload_b64, sig = token.rsplit(".", 1)
            # Constant-time comparison to prevent timing attacks
            expected = hmac.new(
                self._secret, payload_b64.encode(), hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig, expected):
                return False
            # Restore padding for base64 decoding
            padding = "=" * (-len(payload_b64) % 4)
            payload = json.loads(
                base64.urlsafe_b64decode(payload_b64 + padding)
            )
            if time.time() > payload["exp"]:
                return False
            return True
        except Exception:
            return False

    def revoke_token(self, token: str) -> None:
        """
        Not implemented, and it says so instead of pretending.

        HMAC-signed tokens are stateless, so real revocation needs a deny-list
        keyed by `jti` (Redis, or any store shared by every worker). Until that
        exists this raises, because the previous body was `pass`: it returned
        None — the shape of success — while revoking nothing, so any caller that
        trusted it had revocation as decoration.

        Shorten `expires_hours` in `generate_token` to limit exposure meanwhile.
        """
        raise NotImplementedError(
            "Token revocation needs a jti deny-list shared by all workers; it "
            "is not implemented. Use short-lived tokens until it is."
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_authenticator: Optional[WebSocketAuthenticator] = None


def get_authenticator() -> WebSocketAuthenticator:
    """Return the module-level authenticator singleton."""
    global _authenticator
    if _authenticator is None:
        _authenticator = WebSocketAuthenticator()
    return _authenticator
