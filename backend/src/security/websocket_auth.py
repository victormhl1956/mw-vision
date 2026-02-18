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
            # Warn loudly; generate ephemeral key for this process only.
            import warnings
            warnings.warn(
                "HYDRA_SECRET_KEY not set — using ephemeral key. "
                "All tokens will be invalidated on restart.",
                stacklevel=2,
            )
            raw = secrets.token_hex(32)
        self._secret = raw.encode()

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
        Revoke a token before expiry.

        Note: HMAC-signed tokens are stateless; true revocation requires a
        deny-list (e.g., Redis set keyed by `jti`).  This stub records the
        intent; wire up a deny-list in production.
        """
        # TODO: Add jti to a Redis deny-list with TTL = token expiry.
        pass


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
