"""
Trust Manager - Model trust level enforcement for Hydra Protocol.

Security fixes applied (2026-02-17):
  VULN-007: SENSITIVE and CRITICAL fragments are now hard-routed to local
            (TRUSTED) models only.  The prefer_cost_efficiency flag no
            longer overrides the security boundary for sensitive data.
  VULN-010: Unknown model denials are now logged via AuditLogger instead
            of silently returning False.
"""
from typing import Dict, List, Optional
from enum import Enum


class TrustLevel(Enum):
    """Trust levels for AI models."""
    TRUSTED = "trusted"            # Local models (Ollama) — no data leaves the host
    SEMI_TRUSTED = "semi_trusted"  # Commercial with data-processing agreements (Claude, GPT-4)
    UNTRUSTED = "untrusted"        # Foreign jurisdiction or unknown privacy guarantees (DeepSeek)


class TrustManager:
    """Manages model trust levels and routing decisions."""

    # Model trust level configuration
    MODEL_TRUST_LEVELS: Dict[str, TrustLevel] = {
        # Local models — full trust, no network egress
        "ollama-llama3":    TrustLevel.TRUSTED,
        "ollama-codellama": TrustLevel.TRUSTED,
        "ollama-mistral":   TrustLevel.TRUSTED,

        # Commercial — semi-trusted (subject to data retention policies)
        "claude-3-5-sonnet": TrustLevel.SEMI_TRUSTED,
        "claude-3-haiku":    TrustLevel.SEMI_TRUSTED,
        "gpt-4o":            TrustLevel.SEMI_TRUSTED,
        "gpt-4-turbo":       TrustLevel.SEMI_TRUSTED,

        # Foreign jurisdiction — untrusted (GDPR/OSINT privacy risk)
        "deepseek-chat":  TrustLevel.UNTRUSTED,
        "deepseek-coder": TrustLevel.UNTRUSTED,
    }

    # Maximum trust level allowed per sensitivity tier.
    # CRITICAL and SENSITIVE data must stay on local (TRUSTED) models only.
    _SENSITIVITY_MAX_TRUST: Dict[str, TrustLevel] = {
        "CRITICAL":  TrustLevel.TRUSTED,
        "SENSITIVE": TrustLevel.TRUSTED,    # FIX VULN-007: was allowing SEMI_TRUSTED
        "SAFE":      TrustLevel.UNTRUSTED,  # Cloud is acceptable for non-sensitive data
    }

    # OSINT data is restricted to local models regardless of code sensitivity
    OSINT_ALLOWED_MODELS = ["ollama-llama3", "ollama-codellama"]

    # Trust level ordering for comparison
    _TRUST_ORDER: Dict[TrustLevel, int] = {
        TrustLevel.TRUSTED:      2,
        TrustLevel.SEMI_TRUSTED: 1,
        TrustLevel.UNTRUSTED:    0,
    }

    def __init__(self, audit_logger=None):
        # Optional audit logger for VULN-010 fix (unknown model denials)
        self._audit = audit_logger

    def can_process_fragment(self, model: str, sensitivity: str) -> bool:
        """
        Check if a model is permitted to process a code fragment.

        Args:
            model:       Model identifier (must be in MODEL_TRUST_LEVELS)
            sensitivity: Fragment sensitivity ('SAFE', 'SENSITIVE', 'CRITICAL')

        Returns:
            True if the model's trust level meets the sensitivity requirement.
        """
        trust_level = self.MODEL_TRUST_LEVELS.get(model)

        if trust_level is None:
            # Unknown model — deny and log the anomaly (VULN-010 fix)
            if self._audit:
                self._audit.log_event(
                    event_type="SECURITY_ALERT",
                    actor="trust_manager",
                    action="fragment_routing",
                    resource=f"model:{model}",
                    result="DENIED_UNKNOWN_MODEL",
                    metadata={"sensitivity": sensitivity},
                )
            return False

        max_trust = self._SENSITIVITY_MAX_TRUST.get(sensitivity, TrustLevel.TRUSTED)
        return self._TRUST_ORDER[trust_level] >= self._TRUST_ORDER[max_trust]

    def can_process_osint(self, model: str) -> bool:
        """
        Check whether a model is allowed to process OSINT-classified data.

        OSINT data (Venezuela, DGCIM, militia, etc.) is restricted to local
        models exclusively regardless of fragment sensitivity scoring.

        Args:
            model: Model identifier

        Returns:
            True if model is approved for OSINT data.
        """
        return model in self.OSINT_ALLOWED_MODELS

    def get_allowed_models(self, sensitivity: str) -> List[str]:
        """
        Return models permitted for the given sensitivity level.

        Args:
            sensitivity: 'SAFE', 'SENSITIVE', or 'CRITICAL'

        Returns:
            List of allowed model identifiers.
        """
        return [
            model
            for model in self.MODEL_TRUST_LEVELS
            if self.can_process_fragment(model, sensitivity)
        ]

    def route_fragment(
        self, sensitivity: str, prefer_cost_efficiency: bool = True
    ) -> str:
        """
        Select the best model for a fragment given its sensitivity.

        CRITICAL and SENSITIVE fragments are always routed to local Ollama
        models regardless of prefer_cost_efficiency.  Only SAFE fragments
        can be routed to cloud models when cost efficiency is preferred.

        Args:
            sensitivity:            Fragment sensitivity level.
            prefer_cost_efficiency: Prefer cheaper models for SAFE data only.

        Returns:
            Selected model identifier.

        Raises:
            ValueError: If no models are available for the sensitivity level.
        """
        allowed = self.get_allowed_models(sensitivity)

        if not allowed:
            raise ValueError(f"No models available for sensitivity: {sensitivity}")

        # CRITICAL: hard-route to local model, no exceptions
        if sensitivity == "CRITICAL":
            return "ollama-llama3"

        # SENSITIVE: local-only (VULN-007 fix — cost efficiency never applies here)
        if sensitivity == "SENSITIVE":
            local_models = [
                m for m in allowed
                if self.MODEL_TRUST_LEVELS[m] == TrustLevel.TRUSTED
            ]
            return local_models[0] if local_models else allowed[0]

        # SAFE: cost efficiency is acceptable
        if prefer_cost_efficiency and "claude-3-haiku" in allowed:
            return "claude-3-haiku"

        return allowed[0]
