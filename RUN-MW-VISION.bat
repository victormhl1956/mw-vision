@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ============================================
REM    MW-VISION PROFESSIONAL LAUNCHER
REM ============================================
REM Single-click startup for MW-Vision
REM Starts: Backend (8000) + Frontend (5189)
REM ============================================

set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%mw-vision-app"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5189"

REM Create logs directory
if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"
set "LOG_FILE=%PROJECT_DIR%logs\mw-vision.log"

echo [%date% %time%] ========================================= >> "%LOG_FILE%"
echo [%date% %time%] MW-VISION PROFESSIONAL LAUNCHER STARTED >> "%LOG_FILE%"

REM Check if ports are already in use
netstat -ano | findstr ":%BACKEND_PORT% " >nul 2>&1
if !errorlevel! equ 0 (
    echo [WARNING] Port %BACKEND_PORT% is already in use. Checking if backend is running...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT% " ^| findstr "LISTENING"') do (
        echo Backend may already be running (PID: %%a)
    )
) else (
    echo [OK] Port %BACKEND_PORT% is available
)

netstat -ano | findstr ":%FRONTEND_PORT% " >nul 2>&1
if !errorlevel! equ 0 (
    echo [WARNING] Port %FRONTEND_PORT% is already in use.
    echo The frontend may already be running.
    echo.
    echo If you want to restart, please close the existing terminals first.
    echo.
    echo Opening http://localhost:%FRONTEND_PORT% ...
    start http://localhost:%FRONTEND_PORT%
    exit /b 0
)

REM ============================================
REM Check Dependencies
REM ============================================
echo [1/4] Checking Node.js...

where node >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Node.js not found. Please install from https://nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found: %node_path%
for /f "tokens=*" %%i in ('node --version') do echo     Version: %%i

echo [2/4] Checking Python...

where python >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python not found. Please install from https://python.org
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo     Version: %%i

REM ============================================
REM Start Backend
REM ============================================
echo [3/4] Starting Backend Server (port %BACKEND_PORT%)...

cd /d "%BACKEND_DIR%"

REM Check if uvicorn is installed
python -c "import uvicorn" 2>nul
if !errorlevel! neq 0 (
    echo Installing uvicorn...
    pip install uvicorn >nul 2>&1
)

REM Start backend in background window
start "MW-Vision Backend [8000]" cmd /c "echo Starting Backend... && cd /d \"%BACKEND_DIR%\" && uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT%"

REM Wait for backend to start
echo Waiting for backend to initialize...
set "backend_ready=0"
for /l %%i in (1,1,30) do (
    timeout /t 1 /nobreak >nul
    curl -s -o nul -w "%%{http_code}" http://localhost:%BACKEND_PORT%/health --max-time 1 >nul 2>&1
    if !errorlevel! equ 0 (
        set backend_ready=1
        echo [%date% %time%] Backend started successfully >> "%LOG_FILE%"
        echo [OK] Backend ready on http://localhost:%BACKEND_PORT%
        break
    )
)

if !backend_ready! equ 0 (
    echo [WARNING] Backend may not have started properly
    echo Trying to continue anyway...
)

REM ============================================
REM Start Frontend
REM ============================================
echo [4/4] Starting Frontend (port %FRONTEND_PORT%)...

cd /d "%FRONTEND_DIR%"

REM Check if node_modules exists
if not exist "%FRONTEND_DIR%node_modules" (
    echo Installing frontend dependencies...
    npm install --silent
)

REM Start frontend in background window
start "MW-Vision Frontend [%FRONTEND_PORT%]" cmd /c "echo Starting Frontend... && cd /d \"%FRONTEND_DIR%\" && npm run dev -- --port %FRONTEND_PORT% --host"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
set "frontend_ready=0"
for /l %%i in (1,1,30) do (
    timeout /t 2 /nobreak >nul
    curl -s -o nul -w "%%{http_code}" http://localhost:%FRONTEND_PORT%/ --max-time 1 >nul 2>&1
    if !errorlevel! equ 0 (
        set frontend_ready=1
        echo [%date% %time%] Frontend started successfully >> "%LOG_FILE%"
        echo [OK] Frontend ready on http://localhost:%FRONTEND_PORT%
        break
    )
)

REM ============================================
REM Summary
REM ============================================
echo.
echo ============================================
echo    MW-VISION IS READY!
echo ============================================
echo.
echo Access the application at:
echo   http://localhost:%FRONTEND_PORT%
echo.
echo Backend API:
echo   http://localhost:%BACKEND_PORT%
echo   ws://localhost:%BACKEND_PORT%/ws
echo.
echo Health Check:
echo   http://localhost:%BACKEND_PORT%/health
echo.
echo Logs: %PROJECT_DIR%logs\
echo.
echo [%date% %time%] MW-Vision launch complete >> "%LOG_FILE%"

echo Opening application in browser...
start http://localhost:%FRONTEND_PORT%

echo.
echo Both services are running. Keep this window open.
echo To stop: Close the "MW-Vision Backend" and "MW-Vision Frontend" windows
echo.
pause

endlocal
