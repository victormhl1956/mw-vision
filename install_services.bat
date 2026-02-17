@echo off
REM MW-Vision Service Installation Script
REM Installs PM2 and configures auto-start for all services

echo ========================================
echo MW-Vision Service Installation
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if PM2 is installed
echo [1/6] Checking PM2 installation...
npm list -g pm2 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] PM2 not found. Installing globally...
    npm install -g pm2 pm2-windows-startup
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install PM2
        pause
        exit /b 1
    )
    echo [OK] PM2 installed successfully
) else (
    echo [OK] PM2 already installed
)

REM Create logs directory
echo [2/6] Creating logs directory...
if not exist "%~dp0logs" mkdir "%~dp0logs"
echo [OK] Logs directory ready

REM Stop any existing PM2 processes
echo [3/6] Stopping existing MW-Vision services...
pm2 stop mw-vision-backend >nul 2>&1
pm2 stop mw-vision-frontend >nul 2>&1
pm2 stop mw-vision-health-monitor >nul 2>&1
pm2 delete mw-vision-backend >nul 2>&1
pm2 delete mw-vision-frontend >nul 2>&1
pm2 delete mw-vision-health-monitor >nul 2>&1
echo [OK] Cleanup complete

REM Start services via PM2
echo [4/6] Starting MW-Vision services...
pm2 start "%~dp0ecosystem.config.js"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [OK] Services started

REM Save PM2 process list
echo [5/6] Saving PM2 configuration...
pm2 save
echo [OK] Configuration saved

REM Configure auto-start on Windows boot
echo [6/6] Configuring auto-start on boot...
pm2-startup install
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Could not configure auto-start. Run as Administrator to enable.
) else (
    echo [OK] Auto-start configured
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Services running:
pm2 list
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5189
echo.
echo Useful commands:
echo   pm2 list          - Show all services
echo   pm2 logs          - Show live logs
echo   pm2 monit         - Monitor resources
echo   pm2 restart all   - Restart all services
echo   pm2 stop all      - Stop all services
echo.
pause
