# MW-Vision Keep-Alive Script (PowerShell)
# Mantiene el servidor activo con reinicio automático
# Compatible con Windows PowerShell 5.1+

$ErrorActionPreference = "Stop"

$script:APP_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:LOG_FILE = Join-Path $script:APP_DIR "logs\keepalive.log"
$script:PORT = 5189
$script:PID_FILE = Join-Path $script:APP_DIR "vite.pid"

# Crear directorio de logs
$logsDir = Join-Path $script:APP_DIR "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Tee-Object -FilePath $script:LOG_FILE
}

function Test-ServerHealth {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$script:PORT" -TimeoutSec 5 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Stop-OldProcess {
    if (Test-Path $script:PID_FILE) {
        $oldPid = Get-Content $script:PID_FILE -ErrorAction SilentlyContinue
        if ($oldPid) {
            try {
                $process = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Log "Deteniendo proceso anterior (PID: $oldPid)"
                    $process | Stop-Process -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 2
                }
            } catch {
                Write-Log "No se pudo detener el proceso: $_"
            }
        }
        Remove-Item $script:PID_FILE -ErrorAction SilentlyContinue
    }
}

function Start-Server {
    Write-Log "Iniciando servidor Vite..."
    
    $env:PORT = $script:PORT
    
    $process = Start-Process -FilePath "npm" -ArgumentList "run","dev","--","--port",$script:PORT,"--host" -WorkingDirectory $script:APP_DIR -PassThru -NoNewWindow
    
    if ($process) {
        $process.Id | Set-Content $script:PID_FILE
        Write-Log "Servidor iniciado (PID: $($process.Id))"
        Start-Sleep -Seconds 10
        return $true
    }
    return $false
}

function Start-KeepAlive {
    Write-Log "========================================="
    Write-Log "MW-Vision Keep-Alive Script Iniciado"
    Write-Log "Puerto: $script:PORT"
    Write-Log "========================================="
    
    $checkCount = 0
    $restartCount = 0
    $maxRestarts = 10
    
    while ($true) {
        $checkCount++
        Write-Log "Verificación #$checkCount"
        
        if (Test-ServerHealth) {
            Write-Log "Servidor saludable"
        } else {
            Write-Log "Servidor no responde, reiniciando..."
            Stop-OldProcess
            
            if (Start-Server) {
                $restartCount++
                Write-Log "Reinicio #$restartCount completado"
                
                if ($restartCount -ge $maxRestarts) {
                    Write-Log "ADVERTENCIA: Demasiados reinicios ($restartCount), esperando 5 minutos..."
                    Start-Sleep -Seconds 300
                    $restartCount = 0
                }
            } else {
                Write-Log "ERROR: No se pudo iniciar el servidor"
                Start-Sleep -Seconds 30
            }
        }
        
        # Verificar cada 60 segundos
        Write-Log "Esperando 60 segundos..."
        Start-Sleep -Seconds 60
    }
}

# Maneo de Ctrl+C
Write-Log "Presiona Ctrl+C para detener el script"
try {
    Start-KeepAlive
} finally {
    Write-Log "Script detenido"
}
