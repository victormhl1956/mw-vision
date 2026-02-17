"""
Port Monitor for MW-Vision
Ensures backend port 8000 is always listening
Complements PM2 and health monitor
"""

import os
import time
import socket
import logging
import subprocess
from pathlib import Path

# Configuration
BACKEND_PORT = 8000
FRONTEND_PORT = 5189
CHECK_INTERVAL = 30  # seconds
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'port_monitor.log'

# Logging
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def is_port_open(port: int) -> bool:
    """Check if a port is listening"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except Exception as e:
        logger.error(f"Error checking port {port}: {e}")
        return False


def restart_backend():
    """Restart backend via PM2"""
    try:
        result = subprocess.run(
            ['pm2', 'restart', 'mw-vision-backend'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("✅ Backend restarted via PM2")
            return True
        else:
            logger.error(f"❌ Failed to restart backend: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("⏱️ Timeout restarting backend")
        return False
    except FileNotFoundError:
        logger.error("❌ PM2 not found. Install with: npm install -g pm2")
        return False
    except Exception as e:
        logger.error(f"❌ Error restarting backend: {e}")
        return False


def restart_frontend():
    """Restart frontend via PM2"""
    try:
        result = subprocess.run(
            ['pm2', 'restart', 'mw-vision-frontend'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("✅ Frontend restarted via PM2")
            return True
        else:
            logger.error(f"❌ Failed to restart frontend: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Error restarting frontend: {e}")
        return False


def main():
    """Main monitoring loop"""
    logger.info("🔍 Port Monitor started")
    logger.info(f"Monitoring ports: Backend={BACKEND_PORT}, Frontend={FRONTEND_PORT}")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")

    consecutive_backend_failures = 0
    consecutive_frontend_failures = 0
    MAX_FAILURES = 3

    while True:
        try:
            # Check backend port
            if is_port_open(BACKEND_PORT):
                logger.info(f"✅ Backend port {BACKEND_PORT} is listening")
                consecutive_backend_failures = 0
            else:
                consecutive_backend_failures += 1
                logger.warning(f"⚠️ Backend port {BACKEND_PORT} is NOT listening ({consecutive_backend_failures}x)")

                if consecutive_backend_failures >= MAX_FAILURES:
                    logger.error(f"🚨 Backend port down {MAX_FAILURES}x, restarting...")
                    if restart_backend():
                        consecutive_backend_failures = 0
                        time.sleep(10)  # Wait for backend to initialize

            # Check frontend port
            if is_port_open(FRONTEND_PORT):
                logger.info(f"✅ Frontend port {FRONTEND_PORT} is listening")
                consecutive_frontend_failures = 0
            else:
                consecutive_frontend_failures += 1
                logger.warning(f"⚠️ Frontend port {FRONTEND_PORT} is NOT listening ({consecutive_frontend_failures}x)")

                if consecutive_frontend_failures >= MAX_FAILURES:
                    logger.error(f"🚨 Frontend port down {MAX_FAILURES}x, restarting...")
                    if restart_frontend():
                        consecutive_frontend_failures = 0
                        time.sleep(5)

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Port monitor stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
