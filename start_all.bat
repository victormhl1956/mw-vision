@echo off
chcp 65001 >nul
echo ============================================
echo    MW-VISION ALPHA TESTING LAUNCHER
echo ============================================
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Check if Node.js is installed
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python first.
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
cd mw-vision-app
npm install >nul 2>&1
echo [OK] Frontend dependencies ready

cd ..\backend
pip install fastapi uvicorn websockets >nul 2>&1
echo [OK] Backend dependencies ready

echo.
echo [2/3] Starting Backend Server...
start "MW-Vision Backend" cmd /c "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak >nul
echo [OK] Backend started on http://localhost:8000

cd ..\mw-vision-app

echo.
echo [3/3] Starting Frontend...
start "MW-Vision Frontend" cmd /c "npm run dev"
timeout /t 5 /nobreak >nul
echo [OK] Frontend started

echo.
echo ============================================
echo    MW-VISION IS READY!
echo ============================================
echo.
echo Access the application at:
echo   http://localhost:5189
echo.
echo WebSocket endpoint:
echo   ws://localhost:8000/ws
echo.
echo Health check:
echo   http://localhost:8000/health
echo.
echo Press any key to open the browser...
pause >nul
start http://localhost:5189
