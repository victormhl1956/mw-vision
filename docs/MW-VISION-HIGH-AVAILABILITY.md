# MW-Vision High Availability Strategy
## Strategy for 24/7 Uptime

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Purpose:** Keep MW-Vision frontend and backend running continuously without downtime

---

## Executive Summary

This document outlines the strategy to keep MW-Vision running 24/7 without crashes or downtime. The approach includes:

1. **Process Supervision** - Auto-restart on failure
2. **Health Monitoring** - Continuous health checks
3. **Resource Management** - Memory and CPU limits
4. **Logging & Alerting** - Detect issues before they cause downtime

---

## Current Status

The Vite development server is currently running at:
```
Local:   http://localhost:5189/
Network: http://172.23.0.1:5189/
Network: http://10.0.0.236:5189/
```

**Status:** ✅ Running (VITE v6.4.1, ready in 3695 ms)

---

## Solution 1: Keep-Alive Batch Script

### File: `mw-vision-app/keep_alive.bat`

A Windows batch script that monitors the server and restarts it if it crashes.

```batch
@echo off
REM MW-Vision Keep-Alive Script
REM Mantiene el servidor frontend activo con reinicio automático

set "APP_DIR=%~dp0"
set "LOG_FILE=%APP_DIR%logs\keepalive.log"
set "PID_FILE=%APP_DIR%vite.pid"
set "PORT=5189"

:check_loop
    REM Verificar si el servidor está respondiendo
    curl -s -o nul -w "%%{http_code}" http://localhost:%PORT%/ --max-time 5 >nul 2>&1
    if errorlevel 1 (
        echo [%date% %time%] Server not responding, restarting... >> "%LOG_FILE%"
        
        REM Matar proceso anterior si existe
        if exist "%PID_FILE%" (
            for /f %%i in (%PID_FILE%) do taskkill /F /PID %%i >nul 2>&1
            del "%PID_FILE%" >nul 2>&1
        )
        
        REM Iniciar servidor
        cd /d "%APP_DIR%"
        start /B npm run dev -- --port %PORT% --host > "%APP_DIR%logs\vite_output.log" 2>&1
        
        timeout /t 10 /nobreak >nul
    )
    
    REM Verificar cada 60 segundos
    timeout /t 60 /nobreak >nul
goto check_loop
```

### Usage

```cmd
cd l:\nicedev-Project\MW-Vision\mw-vision-app
keep_alive.bat
```

**Note:** Run this as Administrator for best results.

---

## Solution 2: Production Build with PM2 (Recommended)

For true 24/7 operation, use PM2 process manager:

### Installation

```bash
npm install -g pm2
```

### PM2 Ecosystem File

Create `ecosystem.config.js` in `mw-vision-app/`:

```javascript
module.exports = {
  apps: [{
    name: 'mw-vision-frontend',
    script: 'npm',
    args: 'run dev -- --port 5189 --host',
    cwd: './mw-vision-app',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'development',
      PORT: 5189
    },
    exp_backoff_restart_delay: 100,
    max_restarts: 10,
    min_uptime: '5s',
    kill_timeout: 5000,
    listen_timeout: 3000,
    cron_restart: '0 4 * * *',  // Restart at 4 AM daily
  }]
}
```

### Commands

```bash
# Start the app
pm2 start ecosystem.config.js

# Save process list
pm2 save

# Setup startup script
pm2 startup

# View logs
pm2 logs mw-vision-frontend

# Monitor
pm2 monit

# Restart
pm2 restart mw-vision-frontend

# Stop
pm2 stop mw-vision-frontend
```

---

## Solution 3: Windows Service (Most Robust)

For enterprise-grade reliability, run as a Windows Service using NSSM:

### Installation

```bash
# Download NSSM (Non-Sucking Service Manager)
# https://nssm.cc/download

# Or use chocolatey
choco install nssm
```

### Create Service

```cmd
nssm install MW-Vision-Frontend

# Configure:
# Path: C:\Users\<user>\AppData\Roaming\npm\npm.cmd
# Arguments: run dev -- --port 5189 --host
# Working Directory: l:\nicedev-Project\MW-Vision\mw-vision-app
# AppExit: Restart
# I/O Redirect: Set log paths
# Shutdown: Grant shutdown privileges
```

### Service Commands

```cmd
# Start service
nssm start MW-Vision-Frontend

# Stop service
nssm stop MW-Vision-Frontend

# Restart service
nssm restart MW-Vision-Frontend

# Remove service
nssm remove MW-Vision-Frontend
```

---

## Solution 4: Docker Container

For maximum portability and reliability:

### Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
EXPOSE 5189

CMD ["npm", "run", "dev", "--", "--port", "5189", "--host"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  mw-vision:
    build: .
    ports:
      - "5189:5189"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5189"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          memory: 512M
```

### Commands

```bash
# Build and run
docker compose up -d

# View logs
docker compose logs -f

# Restart
docker compose restart mw-vision

# Stop
docker compose down
```

---

## Health Monitoring

### Basic Health Check Script

Create `monitor.sh` (or `.bat` for Windows):

```bash
#!/bin/bash
# Health check script for MW-Vision

URL="http://localhost:5189"
LOG_FILE="/var/log/mw-vision-health.log"

response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$URL")

if [ "$response" != "200" ]; then
    echo "[$(date)] ALERT: Server returned $response" >> "$LOG_FILE"
    # Send notification (email, Slack, etc.)
    # Example: curl -X POST -H 'Content-type: application/json' \
    #   --data "{\"text\":\"MW-Vision is DOWN!\"}" \
    #   https://hooks.slack.com/services/YOUR/WEBHOOK/URL
else
    echo "[$(date)] OK: Server is healthy" >> "$LOG_FILE"
fi
```

### Cron Job (Every 5 Minutes)

```bash
# Edit crontab
crontab -e

# Add health check
*/5 * * * * /path/to/monitor.sh
```

---

## Resource Management

### Memory Limits

Add to `package.json`:

```json
{
  "scripts": {
    "dev": "node --max-old-space-size=256 node_modules/vite/bin/vite.js --port 5189 --host"
  }
}
```

### Vite Config Optimization

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5189,
    host: true,
    hmr: {
      overlay: true
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'zustand']
  }
})
```

---

## Logging Strategy

### Recommended Log Locations

```
mw-vision-app/
├── logs/
│   ├── access.log          # HTTP access log
│   ├── error.log          # Errors only
│   ├── vite_output.log    # Vite server output
│   └── keepalive.log       # Keep-alive script logs
```

### Log Rotation (Windows)

Use PowerShell for log rotation:

```powershell
# Create log rotation script
$LogDir = "l:\nicedev-Project\MW-Vision\mw-vision-app\logs"
$MaxSize = 10MB

Get-ChildItem $LogDir\*.log | Where-Object {
    $_.Length -gt $MaxSize
} | ForEach-Object {
    $newName = $_.Name -replace '\.log$', "_$(Get-Date -Format yyyyMMdd_HHmmss).log"
    Rename-Item $_.FullName $newName
}
```

Schedule with Task Scheduler to run daily.

---

## Alerting Configuration

### Types of Alerts

| Alert Type | Trigger | Action |
|------------|---------|--------|
| **Critical** | Server down > 5 min | SMS/Call |
| **Warning** | Memory > 80% | Email |
| **Info** | Daily restart | Log only |

### Notification Channels

**Slack Webhook:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🚨 MW-Vision is DOWN! Check immediately."}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Email (via sendmail or SMTP):**
```bash
echo "Subject: MW-Vision Alert\n\nServer is down!" | sendmail admin@example.com
```

---

## Recommended Production Setup

### Tier 1: Development (Current)
- **Tool:** Vite dev server
- **Uptime:** 99% (manual restarts)
- **Use Case:** Active development

### Tier 2: Staging / Light Production
- **Tool:** PM2 process manager
- **Uptime:** 99.9% (auto-restart)
- **Use Case:** Demo environments, internal tools

### Tier 3: Production (Recommended)
- **Tool:** Docker + PM2 inside container
- **Uptime:** 99.99% (health checks, auto-healing)
- **Use Case:** Public deployments

---

## Quick Start Commands

### Option A: Keep-Alive Script (Simplest)
```cmd
cd l:\nicedev-Project\MW-Vision\mw-vision-app
keep_alive.bat
```

### Option B: PM2 (Recommended)
```bash
cd l:\nicedev-Project\MW-Vision\mw-vision-app
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### Option C: Docker (Most Robust)
```bash
cd l:\nicedev-Project\MW-Vision
docker compose up -d
docker compose logs -f
```

---

## Troubleshooting

### Server Won't Start

```bash
# Check if port is in use
netstat -ano | findstr :5189

# Kill process on port
taskkill /PID <PID> /F

# Clear Vite cache
rm -rf node_modules/.vite
```

### High Memory Usage

```bash
# Check memory
pm2 monit

# Restart with fresh memory
pm2 restart mw-vision-frontend
```

### Curl Not Found (Windows)

Install curl or use alternative:

```powershell
# PowerShell health check
$response = Invoke-WebRequest -Uri "http://localhost:5189" -TimeoutSec 5
if ($response.StatusCode -ne 200) {
    Write-Host "Server is down!"
}
```

---

## Appendix: Complete PM2 Ecosystem File

```javascript
module.exports = {
  apps: [
    {
      name: 'mw-vision-frontend',
      script: 'npm',
      args: 'run dev -- --port 5189 --host',
      cwd: './mw-vision-app',
      
      // Process management
      instances: 1,
      autorestart: true,
      watch: false,
      
      // Memory limits
      max_memory_restart: '300M',
      
      // Restart policy
      exp_backoff_restart_delay: 100,
      max_restarts: 10,
      min_uptime: '5s',
      
      // Daily restart at 4 AM for cleanup
      cron_restart: '0 4 * * *',
      
      // Environment
      env: {
        NODE_ENV: 'development',
        PORT: 5189
      },
      
      // Logging
      log_file: './logs/pm2.log',
      out_file: './logs/pm2-out.log',
      error_file: './logs/pm2-error.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Graceful shutdown
      kill_timeout: 5000,
      listen_timeout: 3000,
      
      // Monitoring
      pmx: true
    }
  ]
}
```

---

## Summary

| Solution | Reliability | Setup Complexity | Best For |
|----------|-------------|-----------------|----------|
| **Keep-Alive Script** | ⭐⭐ | Easy | Development |
| **PM2** | ⭐⭐⭐⭐ | Medium | Staging |
| **Windows Service (NSSM)** | ⭐⭐⭐⭐ | Medium | Production (Windows) |
| **Docker** | ⭐⭐⭐⭐⭐ | Hard | Cloud/Production |

**Recommendation:** Use **PM2** for most cases - it provides excellent reliability with minimal setup.

---

*Document Version: 1.0*  
*Last Updated: February 14, 2026*  
*One Step Ahead*
