# Hydra Protocol — Security Audit Report

**Date:** 2026-02-17
**Auditor:** Claude Sonnet 4.6 (autonomous code review)
**Scope:** `backend/src/hydra/` + `backend/src/security/`
**Status:** 3 CRITICAL vulnerabilities patched; 4 HIGH, 3 MEDIUM, 2 LOW documented

---

## Executive Summary

The Hydra Protocol contained **3 CRITICAL**, **4 HIGH**, **3 MEDIUM**, and **2 LOW** severity vulnerabilities.

The three CRITICAL issues were patched in this session:

| ID | Severity | File | Issue | Status |
|----|----------|------|-------|--------|
| VULN-001 | **CRITICAL** | websocket_auth.py | `verify_token()` returned `True` unconditionally | ✅ Fixed |
| VULN-002 | **CRITICAL** | websocket_auth.py | Tokens generated but never stored (no verification state) | ✅ Fixed |
| VULN-003 | **CRITICAL** | audit_logger.py | No file locking → concurrent write corruption | ✅ Fixed |
| VULN-007 | **HIGH** | trust_manager.py | SENSITIVE data routed to cloud models for cost efficiency | ✅ Fixed |
| VULN-010 | **MEDIUM** | trust_manager.py | Unknown model denials silently ignored | ✅ Fixed |
| VULN-004 | HIGH | obfuscator.py | MD5 with 8-char truncation as integrity marker | 📋 Documented |
| VULN-005 | HIGH | obfuscator.py | Plaintext variable map returned alongside obfuscated code | 📋 Documented |
| VULN-006 | HIGH | fragmenter.py | Keyword-count classification trivially bypassed | 📋 Documented |
| VULN-008 | MEDIUM | obfuscator.py | Deterministic sequential obfuscation (v1, v2, v3…) | 📋 Documented |
| VULN-009 | MEDIUM | audit_logger.py | Log injection via newlines; day-boundary file routing bug | ✅ Fixed |
| VULN-011 | LOW | fragmenter.py | Mixed credential/OSINT keywords — classification noise | 📋 Documented |
| VULN-012 | LOW | trust_manager.py | No rate limiting on fragment submission | 📋 Documented |

---

## Patched Vulnerabilities — Technical Details

### VULN-001 & VULN-002: Authentication Bypass (websocket_auth.py)

**Before:**
```python
def verify_token(self, token: str) -> bool:
    if os.getenv('ENVIRONMENT') == 'development':
        return len(token) > 10  # Basic sanity check
    return True  # ← Always True in production
```

**After:** HMAC-SHA256 signed tokens with expiry.
- Payload: `{"iat": unix_ts, "exp": unix_ts+86400, "jti": random_hex}`
- Signature: `HMAC-SHA256(secret_key, base64url(payload))`
- `verify_token()` verifies signature via `hmac.compare_digest()` (timing-safe) and checks expiry.
- Unknown tokens → `False`. Expired tokens → `False`. Tampered tokens → `False`.
- `HYDRA_SECRET_KEY` env var required. **Corrected 2026-10-02:** this line used to read "warning emitted if not set", which was the whole problem — a warning in production goes nowhere, and the constructor minted an ephemeral per-process key, so tokens signed by one PM2 worker were rejected by another and the failures looked like network flakiness. The constructor now raises `RuntimeError` at startup if the key is missing, shorter than 32 characters, a known placeholder, or a short pattern repeated to reach the length. `HYDRA_ALLOW_WEAK_KEY=1` is the deliberate, awkward override for reproducing a report locally.

**Test result:** `Short token rejected: True` (was `False` with old code)

---

### VULN-003 & VULN-009: Audit Log Corruption (audit_logger.py)

**Before:** `open(file, 'a')` without locking; log file path cached at init time.

**After:**
- `threading.Lock()` for in-process serialisation.
- `fcntl.flock(LOCK_EX)` for cross-process safety on POSIX (skipped on Windows).
- `os.fsync()` to ensure durability before releasing the lock.
- `_current_log_file()` computes the filename from `datetime.now(timezone.utc)` at each call (fixes day-boundary bug).
- `_sanitize()` strips `\n`, `\r`, `\x00` from metadata values (fixes log injection).

---

### VULN-007: SENSITIVE Data Routed to Cloud (trust_manager.py)

**Before:** `route_fragment("SENSITIVE", prefer_cost_efficiency=True)` returned `claude-3-haiku` (a cloud API model).

**After:** `_SENSITIVITY_MAX_TRUST` maps `SENSITIVE → TRUSTED`, meaning only local Ollama models can receive SENSITIVE or CRITICAL fragments. `prefer_cost_efficiency` only applies to `SAFE` data.

**Test result:** `SENSITIVE fragment routed to: ollama-llama3` (was `claude-3-haiku`)

---

## Remaining Documented Vulnerabilities (Next Sprint)

### VULN-004 — MD5 Integrity Marker (HIGH)
Replace `hashlib.md5(code.encode()).hexdigest()[:8]` with `hmac.new(secret, code.encode(), sha256).hexdigest()[:16]`.
Collision space: current 32-bit (trivial) → HMAC-SHA256 (infeasible).

### VULN-005 — Plaintext Variable Map (HIGH)
`obfuscate()` returns `(obfuscated_code, variable_map)` — the deobfuscation key alongside the ciphertext.
Fix: encrypt the variable map with AES-GCM before returning an opaque token.

### VULN-006 — Keyword-Count Classification (HIGH)
A developer who renames `api_key` to `ak` bypasses the classifier entirely.
Fix: Add Python AST analysis for assignment target names; use filepath-based classification as a primary signal.

### VULN-008 — Deterministic Obfuscation Schema (MEDIUM)
`v1, v2, v3…` naming is predictable and structurally reversible.
Fix: Use randomly-named 8-character identifiers seeded per-obfuscation.

### VULN-011 — Keyword Pollution (LOW)
Split `SENSITIVE_KEYWORDS` into credential keywords (weight 3) and domain keywords (weight 2) with configurable thresholds.

### VULN-012 — No Rate Limiting (LOW)
Add per-connection fragment limits: `MAX_FRAGMENTS_PER_MINUTE = 60`, `MAX_FRAGMENT_SIZE_BYTES = 65536`.

---

## Files Changed

| File | Change |
|------|--------|
| `backend/src/security/websocket_auth.py` | Rewrote token generation/verification with HMAC-SHA256 |
| `backend/src/security/audit_logger.py` | Added threading.Lock + fcntl, dynamic log path, metadata sanitisation |
| `backend/src/hydra/trust_manager.py` | Hard-enforced TRUSTED-only routing for SENSITIVE+CRITICAL; added unknown-model logging |

---

## All Tests Pass

```
=== TEST 1: Code Fragmenter    === [OK] PASSED
=== TEST 2: Trust Manager      === [OK] PASSED  (SENSITIVE → ollama-llama3)
=== TEST 3: Code Obfuscator    === [OK] PASSED
=== TEST 4: Audit Logger       === [OK] PASSED
=== TEST 5: WebSocket Auth     === [OK] PASSED  (Short token rejected: True)
ALL TESTS PASSED
```
