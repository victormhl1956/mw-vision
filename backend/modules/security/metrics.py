"""
Security Metrics Tracking
"""

from datetime import datetime
from typing import Dict, Any


class SecurityMetrics:
    """Thread-safe security metrics tracker"""

    def __init__(self):
        self.data: Dict[str, Any] = {
            "requests_blocked": 0,
            "threats_detected": 0,
            "invalid_messages": 0,
            "start_time": datetime.now().isoformat()
        }

    def increment(self, key: str, amount: int = 1):
        """Increment a metric"""
        if key in self.data:
            self.data[key] += amount

    def get_all(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self.data.copy()

    def reset(self):
        """Reset metrics"""
        self.data = {
            "requests_blocked": 0,
            "threats_detected": 0,
            "invalid_messages": 0,
            "start_time": datetime.now().isoformat()
        }


# Global instance
security_metrics = SecurityMetrics()
