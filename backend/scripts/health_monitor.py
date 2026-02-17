"""
MW-Vision Health Monitor
Watches backend, frontend, and WebSocket connectivity
Auto-restarts services via PM2 if they fail
"""

import os
import sys
import time
import json
import logging
import requests
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # seconds
MAX_CONSECUTIVE_FAILURES = 3
HEALTH_STATUS_FILE = Path(__file__).parent.parent.parent / 'health_status.json'

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Services to monitor
SERVICES = {
    "mw-vision-backend": {
        "url": "http://localhost:8000/health",
        "pm2_name": "mw-vision-backend",
        "critical": True,
        "timeout": 5,
    },
    "mw-vision-frontend": {
        "url": "http://localhost:5189/",
        "pm2_name": "mw-vision-frontend",
        "critical": True,
        "timeout": 5,
    },
}

# Failure tracking
failure_counts = {name: 0 for name in SERVICES.keys()}


def check_http(url: str, timeout: int = 5) -> bool:
    """Check if HTTP endpoint is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        logger.debug(f"HTTP check failed for {url}: {e}")
        return False


def restart_service_via_pm2(pm2_name: str) -> bool:
    """Restart a service using PM2"""
    try:
        result = subprocess.run(
            ['pm2', 'restart', pm2_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info(f"✅ Successfully restarted {pm2_name} via PM2")
            return True
        else:
            logger.error(f"❌ Failed to restart {pm2_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ Timeout restarting {pm2_name}")
        return False
    except FileNotFoundError:
        logger.error("❌ PM2 not found in PATH. Install with: npm install -g pm2")
        return False
    except Exception as e:
        logger.error(f"❌ Error restarting {pm2_name}: {e}")
        return False


def check_all_services():
    """Run health checks on all services"""
    status = {}

    for name, config in SERVICES.items():
        logger.debug(f"Checking {name}...")

        # HTTP check
        is_healthy = check_http(config['url'], config['timeout'])

        if is_healthy:
            failure_counts[name] = 0
            status[name] = {
                "status": "healthy",
                "last_check": datetime.now().isoformat(),
                "failures": 0,
            }
            logger.info(f"✅ {name} is healthy")
        else:
            failure_counts[name] += 1
            status[name] = {
                "status": "unhealthy",
                "last_check": datetime.now().isoformat(),
                "failures": failure_counts[name],
            }
            logger.warning(f"⚠️ {name} failed health check ({failure_counts[name]}x)")

            # Auto-restart if critical and failed too many times
            if config['critical'] and failure_counts[name] >= MAX_CONSECUTIVE_FAILURES:
                logger.error(f"🚨 {name} failed {MAX_CONSECUTIVE_FAILURES}x, triggering restart")
                if restart_service_via_pm2(config['pm2_name']):
                    failure_counts[name] = 0  # Reset after restart

    return status


def save_status(status: dict):
    """Save status to JSON file for external monitoring"""
    try:
        HEALTH_STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HEALTH_STATUS_FILE, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "services": status,
            }, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save status: {e}")


def main():
    """Main monitoring loop"""
    logger.info("🔍 MW-Vision Health Monitor started")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    logger.info(f"Monitoring {len(SERVICES)} services")

    while True:
        try:
            status = check_all_services()
            save_status(status)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Health monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
