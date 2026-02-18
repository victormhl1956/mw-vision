"""
Audit Logger - Security event logging for MW-Vision.

Security fixes applied (2026-02-17):
  VULN-003: Added threading.Lock() + advisory fcntl file locking to
            prevent concurrent write corruption of the JSONL audit trail.
  VULN-009: Log file now computed at write-time (not init-time) to avoid
            day-boundary misrouting.  Metadata is sanitised to prevent
            log-injection via embedded newlines.
"""
import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class AuditLogger:
    """Logs security events for compliance and forensics."""

    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Core write path
    # ------------------------------------------------------------------

    def log_event(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        result: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Append a security event to today's audit log.

        Thread-safe: uses a threading lock + advisory file lock so that
        concurrent writers cannot interleave partial JSON lines.

        Args:
            event_type: Category ('auth', 'data_access', 'model_usage', …)
            actor:      Principal performing the action (IP, user ID, …)
            action:     Verb describing what happened
            resource:   Object of the action
            result:     Outcome ('success', 'denied', 'error')
            metadata:   Arbitrary extra context (will be sanitised)
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": str(event_type),
            "actor": str(actor),
            "action": str(action),
            "resource": str(resource),
            "result": str(result),
            "metadata": self._sanitize(metadata or {}),
        }
        line = json.dumps(event, ensure_ascii=False) + "\n"
        log_file = self._current_log_file()

        with self._lock:
            with open(log_file, "a", encoding="utf-8") as fh:
                # Advisory lock for cross-process safety on POSIX.
                if sys.platform != "win32":
                    import fcntl
                    fcntl.flock(fh, fcntl.LOCK_EX)
                try:
                    fh.write(line)
                    fh.flush()
                    os.fsync(fh.fileno())
                finally:
                    if sys.platform != "win32":
                        import fcntl  # noqa: F811
                        fcntl.flock(fh, fcntl.LOCK_UN)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def log_websocket_connection(self, client_ip: str, token_valid: bool) -> None:
        """Log a WebSocket connection attempt."""
        self.log_event(
            event_type="websocket_auth",
            actor=client_ip,
            action="connect",
            resource="/ws",
            result="success" if token_valid else "denied",
            metadata={"token_valid": token_valid},
        )

    def log_model_usage(
        self,
        model: str,
        fragment_sensitivity: str,
        allowed: bool,
        reasoning: str,
    ) -> None:
        """Log model usage with Hydra Protocol."""
        self.log_event(
            event_type="model_usage",
            actor="system",
            action="route_fragment",
            resource=model,
            result="allowed" if allowed else "blocked",
            metadata={"sensitivity": fragment_sensitivity, "reasoning": reasoning},
        )

    def log_osint_access(self, model: str, allowed: bool) -> None:
        """Log an OSINT data access attempt."""
        self.log_event(
            event_type="osint_access",
            actor="system",
            action="process_osint",
            resource=model,
            result="allowed" if allowed else "blocked",
            metadata={"data_type": "osint-mw"},
        )

    def log_hydra_operation(
        self,
        operation: str,
        filepath: str,
        fragments_count: int,
        critical_count: int,
    ) -> None:
        """Log a Hydra Protocol fragmentation/obfuscation operation."""
        self.log_event(
            event_type="hydra_protocol",
            actor="system",
            action=operation,
            resource=filepath,
            result="success",
            metadata={
                "fragments": fragments_count,
                "critical_fragments": critical_count,
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _current_log_file(self) -> Path:
        """Return today's log file path (computed fresh each call)."""
        return self.log_dir / f"audit_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"

    @staticmethod
    def _sanitize(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strip control characters from all string values to prevent log
        injection via embedded newlines.
        """
        serialised = json.dumps(data, ensure_ascii=False)
        cleaned = serialised.replace("\n", "\\n").replace("\r", "\\r").replace("\x00", "")
        return json.loads(cleaned)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Return the module-level audit logger singleton."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger
