@echo off
REM MW-Vision Keep-Alive Script
REM Mantiene el servidor frontend activo con reinicio automático

set "APP_DIR=%~dp0"
set "LOG_FILE=%APP_DIR%logs\keepalive.log"
set "PID_FILE=%APP_DIR%vite.pid"
set "PORT=5189"

REM Crear directorio de logs si no existe
if not exist "%APP_DIR%logs" mkdir "%APP_DIR%logs"

echo [%date% %time%] === MW-Vision Keep-Alive Started === >> "%LOG_FILE%"

:check_loop
    echo [%date% %time%] Checking server status... >> "%LOG_FILE%"

    REM Verificar si el servidor está respondiendo
    curl -s -o nul -w "%%{http_code}" http://localhost:%PORT%/ --max-time 5 >nul 2>&1
    if errorlevel 1 (
        echo [%date% %time%] Server not responding, restarting... >> "%LOG_FILE%"
        
        REM Matar proceso anterior si existe
        if exist "%PID_FILE%" (
            for /f %%i in (%PID_FILE%) do (
                taskkill /F /PID %%i >nul 2>&1
                echo [%date% %time%] Killed previous Vite process (PID: %%i) >> "%LOG_FILE%"
            )
            del "%PID_FILE%" >nul 2>&1
        )
        
        REM Iniciar servidor en background
        cd /d "%APP_DIR%"
        start /B npm run dev -- --port %PORT% --host > "%APP_DIR%logs\vite_output.log" 2>&1
        
        echo [%date% %time%] Server started >> "%LOG_FILE%"
        
        REM Esperar a que inicie
        timeout /t 10 /nobreak >nul
    ) else (
        echo [%date% %time%] Server is healthy >> "%LOG_FILE%"
    )

    REM Verificar cada 60 segundos
    timeout /t 60 /nobreak >nul
goto check_loop
