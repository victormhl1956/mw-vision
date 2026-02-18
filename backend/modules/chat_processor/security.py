"""Security scanner for chat conversations."""
import re
from dataclasses import dataclass
from typing import List, Dict

from .models import ParsedMessage, SecurityLevel


@dataclass
class SecurityFinding:
    level: str
    type: str
    description: str
    location: str
    remediation: str

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "type": self.type,
            "description": self.description,
            "location": self.location,
            "remediation": self.remediation,
        }


# Quote chars for regex: single-quote and double-quote
_QCHARS = chr(39) + chr(34)

_SECRET_PATTERNS: Dict[str, str] = {
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
    "OpenRouter Key": r"sk-or-v1-[a-zA-Z0-9]{64}",
    "Anthropic Key": r"sk-ant-api03-[a-zA-Z0-9_-]{95}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "GitHub Token": r"ghp_[a-zA-Z0-9]{36}",
    "JWT Token": r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
    "Private Key": r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
    "Generic API Key": r"api[_-]?key[\s:=]+[" + _QCHARS + r"]?([a-zA-Z0-9_-]{20,})[" + _QCHARS + r"]?",
}

_PII_PATTERNS: Dict[str, str] = {
    "SSN": r"\d{3}-\d{2}-\d{4}",
    "Credit Card": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
    "Password literal": r"password\s*=\s*[" + _QCHARS + r"][^" + _QCHARS + r"]{4,}[" + _QCHARS + r"]",
}

_detected_secrets: set = set()


def scan_messages(messages: List[ParsedMessage]) -> List[SecurityFinding]:
    findings: List[SecurityFinding] = []
    for i, msg in enumerate(messages):
        content = msg.content
        for name, pattern in _SECRET_PATTERNS.items():
            for match in re.finditer(pattern, content, re.IGNORECASE):
                val = match.group(0)
                if val not in _detected_secrets:
                    _detected_secrets.add(val)
                    findings.append(SecurityFinding(
                        level=SecurityLevel.CRITICAL.value,
                        type="secret",
                        description=f"{name} detected",
                        location=f"message_{i} ({msg.role})",
                        remediation="Remove secret and rotate it immediately",
                    ))
        for name, pattern in _PII_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                findings.append(SecurityFinding(
                    level=SecurityLevel.HIGH.value,
                    type="pii",
                    description=f"{name} detected",
                    location=f"message_{i} ({msg.role})",
                    remediation="Remove PII or ensure GDPR compliance",
                ))
    return findings
