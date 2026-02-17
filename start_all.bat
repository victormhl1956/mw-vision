@echo off
REM MW-Vision Quick Start Script
REM Starts all services via PM2

echo Starting MW-Vision services...
echo.

REM Check if PM2 is installed
where pm2 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PM2 not installed. Run install_services.bat first.
    pause
    exit /b 1
)

REM Start services
pm2 start "%~dp0ecosystem.config.js"

echo.
echo Services started!
echo.
pm2 list
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5189
echo.
echo Run 'pm2 logs' to see live logs
echo Run 'pm2 monit' to monitor resources
echo.
pause
