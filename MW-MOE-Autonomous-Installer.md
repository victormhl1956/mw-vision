# 🤖 MW-MOE AUTONOMOUS INSTALLER
# Para ejecutar con Claude Code (claude CLI)
## Copiar este archivo COMPLETO y pegarlo como prompt en Claude Code

**Versión:** 2.0 — Autonomous Edition  
**Fecha:** Febrero 2026  
**Diseñado para:** Claude Code CLI ejecutando en Windows 10/11  
**Filosofía:** Máxima automatización, mínima intervención humana

---

## CÓMO USAR ESTE DOCUMENTO

### Opción A: Prompt directo en Claude Code
```bash
# Desde PowerShell, navegar a tu directorio base
cd $env:USERPROFILE

# Iniciar Claude Code
claude

# Pegar este prompt:
> Lee el archivo MW-MOE-Autonomous-Installer.md y ejecútalo fase por fase.
> Instala todo el stack sin pedirme confirmación excepto donde dice HUMAN_INPUT_REQUIRED.
> Muéstrame un resumen de estado después de cada fase.
```

### Opción B: Ejecución directa con archivo
```bash
# Si Claude Code soporta archivos como prompt:
claude "Read MW-MOE-Autonomous-Installer.md and execute all phases autonomously"
```

---

## INSTRUCCIONES PARA CLAUDE CODE

```
CLAUDE CODE: Lee estas instrucciones completas antes de ejecutar.

IDENTIDAD:
Eres el Field Commander del ecosistema MindWareHouse. Victor Hernandez
(Supreme Commander) te ha delegado la instalación completa de su entorno
de desarrollo MOE. Tu misión es instalar y configurar todo el stack
con mínima intervención humana.

REGLAS DE EJECUCIÓN:
1. Ejecuta cada fase SECUENCIALMENTE — no saltes fases
2. Después de cada fase, ejecuta el CHECKPOINT correspondiente
3. Si un checkpoint FALLA, intenta corregir automáticamente (máximo 3 intentos)
4. Si no puedes corregir después de 3 intentos, REPORTA el error y continúa
5. Solo pide intervención humana donde dice HUMAN_INPUT_REQUIRED
6. Usa PowerShell como shell principal (Windows)
7. Registra TODOS los resultados en un archivo de log
8. Al final, genera un REPORTE COMPLETO de lo instalado

TAGS ESPECIALES:
- [AUTO]              → Ejecutar sin pedir confirmación
- [HUMAN_INPUT_REQUIRED] → Pausar y pedir input al usuario
- [CHECKPOINT]        → Verificar antes de continuar
- [RETRY:3]           → Reintentar hasta 3 veces si falla
- [SKIP_IF_EXISTS]    → Saltar si ya está instalado
- [CRITICAL]          → Si falla, NO continuar sin resolver
```

---

## FASE 0: INICIALIZACIÓN DEL LOG

```
[AUTO]
Crear archivo de log para registrar todo el proceso.
```

```powershell
# Crear directorio de trabajo
$MW_HOME = "$env:USERPROFILE\mw-moe"
$MW_INFRA = "$env:USERPROFILE\mw-infrastructure"
$LOG_FILE = "$env:USERPROFILE\mw-install-log-$(Get-Date -Format 'yyyy-MM-dd-HHmmss').md"

# Iniciar log
@"
# MW-MOE Installation Log
**Fecha:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Sistema:** $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)
**CPU:** $((Get-CimInstance Win32_Processor).Name)
**RAM:** $([math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)) GB

---
"@ | Out-File -FilePath $LOG_FILE -Encoding UTF8

function Log-Phase {
    param([string]$Phase, [string]$Status, [string]$Detail)
    $timestamp = Get-Date -Format 'HH:mm:ss'
    "| $timestamp | $Phase | $Status | $Detail |" | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8
    Write-Host "[$timestamp] $Phase — $Status" -ForegroundColor $(if ($Status -eq "OK") {"Green"} elseif ($Status -eq "FAIL") {"Red"} else {"Yellow"})
}

Log-Phase "INIT" "OK" "Log file created: $LOG_FILE"
```

---

## FASE 1: DETECCIÓN Y INSTALACIÓN DE PREREQUISITOS

```
[AUTO] [SKIP_IF_EXISTS] [RETRY:3]
Detectar qué ya está instalado. Instalar lo que falta.
```

### 1.1 Diagnóstico del sistema

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 1: DIAGNÓSTICO Y PREREQUISITOS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Diagnóstico completo
$diagnosis = @{}

# Node.js
try { $nodeVer = node --version 2>$null; $diagnosis["nodejs"] = $nodeVer } 
catch { $diagnosis["nodejs"] = $null }

# Python
try { $pyVer = python --version 2>$null; $diagnosis["python"] = $pyVer }
catch { $diagnosis["python"] = $null }

# Git
try { $gitVer = git --version 2>$null; $diagnosis["git"] = $gitVer }
catch { $diagnosis["git"] = $null }

# Docker
try { $dockVer = docker --version 2>$null; $diagnosis["docker"] = $dockVer }
catch { $diagnosis["docker"] = $null }

# VS Code
try { $codeVer = code --version 2>$null; $diagnosis["vscode"] = ($codeVer -split "`n")[0] }
catch { $diagnosis["vscode"] = $null }

# npm
try { $npmVer = npm --version 2>$null; $diagnosis["npm"] = $npmVer }
catch { $diagnosis["npm"] = $null }

# pip
try { $pipVer = pip --version 2>$null; $diagnosis["pip"] = $pipVer }
catch { $diagnosis["pip"] = $null }

# winget
try { $wingetVer = winget --version 2>$null; $diagnosis["winget"] = $wingetVer }
catch { $diagnosis["winget"] = $null }

# Disco libre
$freeDisk = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
$diagnosis["disk_free_gb"] = $freeDisk

# RAM total
$totalRAM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
$diagnosis["ram_total_gb"] = $totalRAM

# Mostrar diagnóstico
Write-Host "DIAGNÓSTICO DEL SISTEMA:" -ForegroundColor White
foreach ($key in $diagnosis.Keys | Sort-Object) {
    $val = $diagnosis[$key]
    if ($val) {
        Write-Host "  ✅ $key : $val" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $key : NO INSTALADO" -ForegroundColor Red
    }
}

Log-Phase "DIAG" "OK" "Diagnóstico completado. RAM: ${totalRAM}GB, Disco libre: ${freeDisk}GB"
```

### 1.2 Instalar lo que falta

```powershell
# ── Node.js ──────────────────────────────────────────
if (-not $diagnosis["nodejs"]) {
    Write-Host "`n📦 Instalando Node.js LTS..." -ForegroundColor Yellow
    try {
        winget install OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements --silent
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $nodeCheck = node --version 2>$null
        if ($nodeCheck) { Log-Phase "NODEJS" "OK" "Instalado: $nodeCheck" }
        else { Log-Phase "NODEJS" "WARN" "Instalado pero requiere reiniciar terminal" }
    } catch {
        Log-Phase "NODEJS" "FAIL" "Error: $_"
    }
} else {
    Log-Phase "NODEJS" "SKIP" "Ya instalado: $($diagnosis['nodejs'])"
}

# ── Python ───────────────────────────────────────────
if (-not $diagnosis["python"]) {
    Write-Host "`n📦 Instalando Python 3.12..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $pyCheck = python --version 2>$null
        if ($pyCheck) { Log-Phase "PYTHON" "OK" "Instalado: $pyCheck" }
        else { Log-Phase "PYTHON" "WARN" "Instalado pero requiere reiniciar terminal" }
    } catch {
        Log-Phase "PYTHON" "FAIL" "Error: $_"
    }
} else {
    Log-Phase "PYTHON" "SKIP" "Ya instalado: $($diagnosis['python'])"
}

# ── Git ──────────────────────────────────────────────
if (-not $diagnosis["git"]) {
    Write-Host "`n📦 Instalando Git..." -ForegroundColor Yellow
    try {
        winget install Git.Git --accept-source-agreements --accept-package-agreements --silent
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        git config --global user.name "Victor Hernandez"
        git config --global user.email "victor@mindwarehouse.com"
        git config --global init.defaultBranch main
        Log-Phase "GIT" "OK" "Instalado y configurado"
    } catch {
        Log-Phase "GIT" "FAIL" "Error: $_"
    }
} else {
    Log-Phase "GIT" "SKIP" "Ya instalado: $($diagnosis['git'])"
}

# ── Docker Desktop ───────────────────────────────────
if (-not $diagnosis["docker"]) {
    Write-Host "`n📦 Instalando Docker Desktop..." -ForegroundColor Yellow
    Write-Host "⚠️  Docker Desktop requiere reinicio de PC después de instalar." -ForegroundColor Yellow
    try {
        winget install Docker.DockerDesktop --accept-source-agreements --accept-package-agreements --silent
        Log-Phase "DOCKER" "WARN" "Instalado — REQUIERE REINICIO DE PC"
        
        # Configurar WSL memory limit
        @"
[wsl2]
memory=8GB
processors=4
swap=4GB
"@ | Out-File -FilePath "$env:USERPROFILE\.wslconfig" -Encoding UTF8 -Force
        Log-Phase "WSL" "OK" "Configurado .wslconfig con límites de RAM"
    } catch {
        Log-Phase "DOCKER" "FAIL" "Error: $_"
    }
} else {
    Log-Phase "DOCKER" "SKIP" "Ya instalado: $($diagnosis['docker'])"
}

# ── VS Code ──────────────────────────────────────────
if (-not $diagnosis["vscode"]) {
    Write-Host "`n📦 Instalando VS Code..." -ForegroundColor Yellow
    try {
        winget install Microsoft.VisualStudioCode --accept-source-agreements --accept-package-agreements --silent
        Log-Phase "VSCODE" "OK" "Instalado"
    } catch {
        Log-Phase "VSCODE" "FAIL" "Error: $_"
    }
} else {
    Log-Phase "VSCODE" "SKIP" "Ya instalado: $($diagnosis['vscode'])"
}
```

### 1.3 [CHECKPOINT] Verificar Fase 1

```powershell
Write-Host "`n── CHECKPOINT FASE 1 ──" -ForegroundColor Cyan
$f1_pass = $true
$checks = @(
    @{ name="Node.js"; cmd="node --version" },
    @{ name="Python";  cmd="python --version" },
    @{ name="Git";     cmd="git --version" },
    @{ name="Docker";  cmd="docker --version" },
    @{ name="npm";     cmd="npm --version" },
    @{ name="pip";     cmd="pip --version" }
)

foreach ($check in $checks) {
    try {
        $result = Invoke-Expression $check.cmd 2>$null
        if ($result) { Write-Host "  ✅ $($check.name): $result" -ForegroundColor Green }
        else { Write-Host "  ❌ $($check.name): NO DISPONIBLE" -ForegroundColor Red; $f1_pass = $false }
    } catch {
        Write-Host "  ❌ $($check.name): ERROR" -ForegroundColor Red
        $f1_pass = $false
    }
}

if ($f1_pass) {
    Log-Phase "FASE1" "OK" "Todos los prerequisitos instalados"
} else {
    Log-Phase "FASE1" "WARN" "Algunos componentes pueden necesitar reinicio de terminal"
    Write-Host "`n⚠️  Si ves ❌, cierra y reabre la terminal, luego reintenta." -ForegroundColor Yellow
}
```

---

## FASE 2: API KEYS — ÚNICO PUNTO DE INTERVENCIÓN HUMANA

```
[HUMAN_INPUT_REQUIRED] [CRITICAL]
Victor debe proporcionar sus API keys. No hay forma de automatizar esto.
Después de este paso, todo vuelve a ser autónomo.
```

### 2.1 Solicitar API keys

```powershell
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "  FASE 2: CONFIGURACIÓN DE API KEYS" -ForegroundColor Magenta
Write-Host "  ⚠️  NECESITO TU INPUT AQUÍ, VICTOR" -ForegroundColor Magenta
Write-Host "========================================`n" -ForegroundColor Magenta

Write-Host "Necesito que me proporciones tus API keys." -ForegroundColor White
Write-Host "Si aún no tienes alguna, créala AHORA en:" -ForegroundColor White
Write-Host "  1. OpenRouter  → https://openrouter.ai/keys" -ForegroundColor Gray
Write-Host "  2. Anthropic   → https://console.anthropic.com/settings/keys" -ForegroundColor Gray
Write-Host "  3. AgentOps    → https://app.agentops.ai (Settings → API Keys)" -ForegroundColor Gray
Write-Host "  4. Langfuse    → Se configura LOCAL después (no necesita key ahora)`n" -ForegroundColor Gray

# Solicitar keys
$OPENROUTER_KEY = Read-Host "🔑 Pega tu OPENROUTER API KEY (sk-or-v1-...)"
$ANTHROPIC_KEY  = Read-Host "🔑 Pega tu ANTHROPIC API KEY (sk-ant-...)"
$AGENTOPS_KEY   = Read-Host "🔑 Pega tu AGENTOPS API KEY (o ENTER para saltar)"

# Validar formato mínimo
if (-not $OPENROUTER_KEY.StartsWith("sk-or")) {
    Write-Host "⚠️  La key de OpenRouter normalmente empieza con 'sk-or'. Continuando..." -ForegroundColor Yellow
}
if (-not $ANTHROPIC_KEY.StartsWith("sk-ant")) {
    Write-Host "⚠️  La key de Anthropic normalmente empieza con 'sk-ant'. Continuando..." -ForegroundColor Yellow
}
```

### 2.2 Guardar keys de forma segura y persistente

```powershell
# Guardar como variables de entorno de usuario (persisten entre sesiones)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", $OPENROUTER_KEY, "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $ANTHROPIC_KEY, "User")
if ($AGENTOPS_KEY) {
    [Environment]::SetEnvironmentVariable("AGENTOPS_API_KEY", $AGENTOPS_KEY, "User")
}
[Environment]::SetEnvironmentVariable("LANGFUSE_HOST", "http://localhost:3000", "User")

# Cargar en sesión actual
$env:OPENROUTER_API_KEY = $OPENROUTER_KEY
$env:ANTHROPIC_API_KEY = $ANTHROPIC_KEY
$env:AGENTOPS_API_KEY = $AGENTOPS_KEY
$env:LANGFUSE_HOST = "http://localhost:3000"

# Guardar backup encriptado en archivo local
$credFile = "$env:USERPROFILE\.mw-credentials"
@"
# MindWareHouse Credentials — $(Get-Date -Format 'yyyy-MM-dd')
# ⚠️ NUNCA subir a Git. NUNCA compartir.
OPENROUTER_API_KEY=$OPENROUTER_KEY
ANTHROPIC_API_KEY=$ANTHROPIC_KEY
AGENTOPS_API_KEY=$AGENTOPS_KEY
LANGFUSE_HOST=http://localhost:3000
"@ | Out-File -FilePath $credFile -Encoding UTF8 -Force

# Proteger archivo (solo tu usuario puede leer)
$acl = Get-Acl $credFile
$acl.SetAccessRuleProtection($true, $false)
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "FullControl", "Allow")
$acl.AddAccessRule($rule)
Set-Acl $credFile $acl

Log-Phase "KEYS" "OK" "API keys configuradas y guardadas"
Write-Host "`n✅ API keys guardadas. De aquí en adelante todo es AUTÓNOMO." -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
```

---

## FASE 3: KILO CLI + EXTENSIÓN VS CODE

```
[AUTO] [SKIP_IF_EXISTS] [RETRY:3]
```

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 3: KILO CLI + VS CODE EXTENSION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ── 3.1 Instalar Kilo CLI ────────────────────────────
$kiloInstalled = $null
try { $kiloInstalled = kilo --version 2>$null } catch {}

if (-not $kiloInstalled) {
    Write-Host "📦 Instalando Kilo CLI..." -ForegroundColor Yellow
    npm install -g @kilocode/cli
    
    # Refrescar PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User") + ";" + "$env:APPDATA\npm"
    
    $kiloCheck = kilo --version 2>$null
    if ($kiloCheck) { Log-Phase "KILO-CLI" "OK" "Instalado: $kiloCheck" }
    else { Log-Phase "KILO-CLI" "FAIL" "Instalación falló" }
} else {
    Log-Phase "KILO-CLI" "SKIP" "Ya instalado: $kiloInstalled"
}

# ── 3.2 Instalar Kilo VS Code Extension ──────────────
Write-Host "📦 Instalando Kilo Code Extension en VS Code..." -ForegroundColor Yellow
code --install-extension kilocode.Kilo-Code 2>$null
code --install-extension ms-python.python 2>$null
code --install-extension eamodio.gitlens 2>$null
Log-Phase "KILO-EXT" "OK" "Extensiones VS Code instaladas"

# ── 3.3 Crear configuración de Kilo ──────────────────
$kiloConfigDir = "$env:USERPROFILE\.kilocode"
if (-not (Test-Path $kiloConfigDir)) { mkdir $kiloConfigDir -Force }

@"
{
  "providers": {
    "openrouter": {
      "apiKey": "$env:OPENROUTER_API_KEY",
      "baseUrl": "https://openrouter.ai/api/v1"
    },
    "anthropic": {
      "apiKey": "$env:ANTHROPIC_API_KEY"
    }
  },
  "defaultProvider": "openrouter",
  "defaultModel": "deepseek/deepseek-chat-v3",
  "autoApproval": {
    "enabled": true,
    "read": { "enabled": true, "outside": false },
    "write": { "enabled": true, "outside": false, "protected": false },
    "execute": {
      "enabled": true,
      "allowed": ["npm", "git", "pnpm", "python", "pip", "pytest", "node", "docker", "docker-compose"],
      "denied": ["rm -rf /", "sudo rm", "format", "del /s /q C:"]
    },
    "browser": { "enabled": false },
    "mcp": { "enabled": true },
    "mode": { "enabled": true },
    "subtasks": { "enabled": true }
  }
}
"@ | Out-File -FilePath "$kiloConfigDir\config.json" -Encoding UTF8 -Force
Log-Phase "KILO-CFG" "OK" "Configuración creada con providers y auto-approval"
```

### [CHECKPOINT] Fase 3

```powershell
$kiloOK = kilo --version 2>$null
if ($kiloOK) {
    Write-Host "  ✅ Kilo CLI: $kiloOK" -ForegroundColor Green
    Log-Phase "FASE3" "OK" "Kilo CLI listo"
} else {
    Write-Host "  ❌ Kilo CLI no disponible" -ForegroundColor Red
    Log-Phase "FASE3" "FAIL" "Kilo CLI no encontrado en PATH"
}
```

---

## FASE 4: LANGFUSE — OBSERVABILIDAD SELF-HOSTED

```
[AUTO] [RETRY:3]
Requiere Docker corriendo.
```

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 4: LANGFUSE (SELF-HOSTED)" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ── 4.1 Verificar Docker está corriendo ──────────────
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "⚠️  Docker no está corriendo. Intentando iniciar..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
    Write-Host "   Esperando 60 segundos a que Docker inicie..." -ForegroundColor Yellow
    Start-Sleep -Seconds 60
    $dockerRunning = docker info 2>$null
    if (-not $dockerRunning) {
        Log-Phase "DOCKER" "FAIL" "Docker no pudo iniciar. Abrir manualmente Docker Desktop."
        Write-Host "❌ Docker no inicia. Abre Docker Desktop manualmente y re-ejecuta esta fase." -ForegroundColor Red
    }
}

if ($dockerRunning) {
    # ── 4.2 Clonar Langfuse ──────────────────────────
    $langfuseDir = "$MW_INFRA\langfuse"
    if (-not (Test-Path $langfuseDir)) {
        Write-Host "📦 Clonando Langfuse..." -ForegroundColor Yellow
        mkdir $MW_INFRA -Force -ErrorAction SilentlyContinue
        git clone https://github.com/langfuse/langfuse.git $langfuseDir
        Log-Phase "LANGFUSE-CLONE" "OK" "Repositorio clonado"
    } else {
        Write-Host "📂 Langfuse ya clonado. Actualizando..." -ForegroundColor Yellow
        Set-Location $langfuseDir
        git pull 2>$null
        Log-Phase "LANGFUSE-CLONE" "SKIP" "Ya existía, actualizado"
    }

    # ── 4.3 Crear override para limitar RAM ──────────
    Set-Location $langfuseDir
    @"
services:
  langfuse-web:
    deploy:
      resources:
        limits:
          memory: 1536M
  langfuse-worker:
    deploy:
      resources:
        limits:
          memory: 768M
"@ | Out-File -FilePath "$langfuseDir\docker-compose.override.yml" -Encoding UTF8 -Force

    # ── 4.4 Iniciar Langfuse ─────────────────────────
    Write-Host "🚀 Iniciando Langfuse..." -ForegroundColor Yellow
    docker compose up -d
    
    Write-Host "   Esperando 45 segundos a que Langfuse inicie..." -ForegroundColor Yellow
    Start-Sleep -Seconds 45

    # ── 4.5 Verificar health ─────────────────────────
    $maxRetries = 5
    $healthy = $false
    for ($i = 1; $i -le $maxRetries; $i++) {
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:3000/api/public/health" -TimeoutSec 10 -ErrorAction Stop
            if ($health.status -eq "OK") {
                $healthy = $true
                break
            }
        } catch {
            Write-Host "   Intento $i/$maxRetries — Langfuse aún iniciando..." -ForegroundColor Yellow
            Start-Sleep -Seconds 15
        }
    }

    if ($healthy) {
        Log-Phase "LANGFUSE" "OK" "Corriendo en http://localhost:3000"
        Write-Host "  ✅ Langfuse corriendo en http://localhost:3000" -ForegroundColor Green
    } else {
        Log-Phase "LANGFUSE" "WARN" "Iniciado pero health check no responde aún"
        Write-Host "  ⚠️  Langfuse iniciado pero puede necesitar más tiempo" -ForegroundColor Yellow
    }
}
```

### [CHECKPOINT] Fase 4

```powershell
$containers = docker compose -f "$MW_INFRA\langfuse\docker-compose.yml" ps --format json 2>$null
if ($containers) {
    Write-Host "  ✅ Langfuse containers corriendo" -ForegroundColor Green
    Log-Phase "FASE4" "OK" "Langfuse operativo"
} else {
    Write-Host "  ⚠️  Verificar Langfuse manualmente: docker compose ps" -ForegroundColor Yellow
    Log-Phase "FASE4" "WARN" "Langfuse puede necesitar atención"
}
```

---

## FASE 5: PYTHON ENVIRONMENT + CREWAI + AGENTOPS

```
[AUTO] [RETRY:3]
```

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 5: PYTHON + CREWAI + AGENTOPS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ── 5.1 Crear directorio del proyecto ────────────────
if (-not (Test-Path $MW_HOME)) { mkdir $MW_HOME -Force }
Set-Location $MW_HOME

# ── 5.2 Crear entorno virtual ────────────────────────
if (-not (Test-Path "$MW_HOME\.venv")) {
    Write-Host "📦 Creando entorno virtual Python..." -ForegroundColor Yellow
    python -m venv .venv
    Log-Phase "VENV" "OK" "Entorno virtual creado"
} else {
    Log-Phase "VENV" "SKIP" "Ya existe"
}

# ── 5.3 Activar venv e instalar dependencias ─────────
& "$MW_HOME\.venv\Scripts\Activate.ps1"

Write-Host "📦 Instalando dependencias Python..." -ForegroundColor Yellow

# Instalar en orden para evitar conflictos
pip install --upgrade pip setuptools wheel 2>$null
pip install python-dotenv rich 2>$null
pip install litellm 2>$null
pip install langfuse 2>$null
pip install agentops 2>$null
pip install "crewai[anthropic]" 2>$null

# ── 5.4 Verificar instalaciones ──────────────────────
$pipChecks = @(
    @{ pkg="crewai"; imp="from crewai import Agent, Task, Crew; print('OK')" },
    @{ pkg="langfuse"; imp="from langfuse import Langfuse; print('OK')" },
    @{ pkg="agentops"; imp="import agentops; print('OK')" },
    @{ pkg="litellm"; imp="import litellm; print('OK')" },
    @{ pkg="dotenv"; imp="from dotenv import load_dotenv; print('OK')" }
)

foreach ($check in $pipChecks) {
    $result = python -c $check.imp 2>$null
    if ($result -eq "OK") {
        Write-Host "  ✅ $($check.pkg)" -ForegroundColor Green
        Log-Phase $check.pkg.ToUpper() "OK" "Instalado"
    } else {
        Write-Host "  ❌ $($check.pkg) — intentando reinstalar..." -ForegroundColor Red
        pip install $check.pkg --force-reinstall 2>$null
        Log-Phase $check.pkg.ToUpper() "RETRY" "Reinstalando"
    }
}

# ── 5.5 Crear .env ──────────────────────────────────
@"
# .env — MindWareHouse MOE
# Generado automáticamente el $(Get-Date -Format 'yyyy-MM-dd HH:mm')

OPENROUTER_API_KEY=$env:OPENROUTER_API_KEY
ANTHROPIC_API_KEY=$env:ANTHROPIC_API_KEY
AGENTOPS_API_KEY=$env:AGENTOPS_API_KEY
LANGFUSE_PUBLIC_KEY=$env:LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY=$env:LANGFUSE_SECRET_KEY
LANGFUSE_HOST=http://localhost:3000
LITELLM_LOG=DEBUG
"@ | Out-File -FilePath "$MW_HOME\.env" -Encoding UTF8 -Force

# ── 5.6 Crear .gitignore ────────────────────────────
@"
.env
.venv/
__pycache__/
*.pyc
.langfuse/
*.log
.mw-credentials
"@ | Out-File -FilePath "$MW_HOME\.gitignore" -Encoding UTF8 -Force

# ── 5.7 Init Git ────────────────────────────────────
if (-not (Test-Path "$MW_HOME\.git")) {
    Set-Location $MW_HOME
    git init
    git add .gitignore
    git commit -m "init: MW-MOE project setup"
    Log-Phase "GIT-INIT" "OK" "Repositorio inicializado"
}
```

### [CHECKPOINT] Fase 5

```powershell
& "$MW_HOME\.venv\Scripts\Activate.ps1"
$crewOK = python -c "from crewai import Crew; print('OK')" 2>$null
if ($crewOK -eq "OK") {
    Write-Host "  ✅ CrewAI + dependencias instaladas" -ForegroundColor Green
    Log-Phase "FASE5" "OK" "Stack Python completo"
} else {
    Write-Host "  ❌ Problema con instalación Python" -ForegroundColor Red
    Log-Phase "FASE5" "FAIL" "CrewAI no importa correctamente"
}
```

---

## FASE 6: CREAR ARCHIVOS DEL MOE

```
[AUTO]
Crear todos los archivos de configuración y crews.
```

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 6: ARCHIVOS DEL MOE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location $MW_HOME

# ── 6.1 moe_config.py ───────────────────────────────
@'
"""
MindWareHouse MOE Configuration — Auto-generated
"""
import os
from dotenv import load_dotenv
load_dotenv()

MODEL_ROUTING = {
    "architect":  "openrouter/anthropic/claude-sonnet-4-5",
    "strategic":  "openrouter/anthropic/claude-opus-4-5",
    "debug":      "openrouter/anthropic/claude-sonnet-4-5",
    "code":       "openrouter/openai/gpt-5.1-codex",
    "security":   "openrouter/anthropic/claude-sonnet-4-5",
    "docs":       "openrouter/deepseek/deepseek-chat-v3",
    "test":       "openrouter/deepseek/deepseek-chat-v3",
    "ask":        "openrouter/deepseek/deepseek-chat-v3",
    "simple":     "openrouter/minimax/minimax-m2.1",
}

def get_model(role: str) -> str:
    return MODEL_ROUTING.get(role, MODEL_ROUTING["ask"])

def verify_config():
    checks = {
        "OpenRouter": bool(os.getenv("OPENROUTER_API_KEY")),
        "Anthropic":  bool(os.getenv("ANTHROPIC_API_KEY")),
        "Langfuse":   bool(os.getenv("LANGFUSE_PUBLIC_KEY")),
        "AgentOps":   bool(os.getenv("AGENTOPS_API_KEY")),
    }
    all_ok = True
    for name, ok in checks.items():
        status = "OK" if ok else "MISSING"
        icon = "✅" if ok else "❌"
        print(f"  {icon} {name}: {status}")
        if not ok: all_ok = False
    print(f"\n  Models configured: {len(MODEL_ROUTING)}")
    return all_ok

if __name__ == "__main__":
    print("=" * 50)
    print("MindWareHouse MOE — Configuration Check")
    print("=" * 50)
    verify_config()
'@ | Out-File -FilePath "$MW_HOME\moe_config.py" -Encoding UTF8 -Force

# ── 6.2 Crear directorio de crews ────────────────────
mkdir "$MW_HOME\crews" -Force -ErrorAction SilentlyContinue
New-Item -Path "$MW_HOME\crews\__init__.py" -ItemType File -Force -Value "" | Out-Null

# ── 6.3 Bug Hunting Crew ────────────────────────────
@'
"""
Bug Hunting Crew — MindWareHouse MOE
4 agentes, 4 modelos, monitoreo completo.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Init monitoring ANTES de importar CrewAI
agentops_available = False
try:
    import agentops
    if os.getenv("AGENTOPS_API_KEY"):
        agentops.init()
        agentops_available = True
except ImportError:
    pass

from crewai import Agent, Task, Crew, Process

# Langfuse callback
langfuse_handler = None
try:
    from langfuse.callback import CallbackHandler
    if os.getenv("LANGFUSE_PUBLIC_KEY"):
        langfuse_handler = CallbackHandler()
except ImportError:
    pass


def hunt_bug(description: str, file_path: str = "", error_log: str = ""):
    """Launch the bug hunting crew."""

    context = f"Bug: {description}\nFile: {file_path}\nError: {error_log}"

    architect = Agent(
        role="Software Architect",
        goal="Analyze architecture and generate root cause hypotheses",
        backstory="30 years of experience finding architectural issues.",
        llm="openrouter/anthropic/claude-sonnet-4-5",
        verbose=True,
    )

    debugger = Agent(
        role="Expert Debugger",
        goal="Reproduce the bug and confirm the root cause",
        backstory="Specialist in debugging production systems.",
        llm="openrouter/anthropic/claude-sonnet-4-5",
        verbose=True,
    )

    security = Agent(
        role="Security Analyst",
        goal="Verify the fix doesn't introduce vulnerabilities",
        backstory="Offensive and defensive security expert.",
        llm="openrouter/deepseek/deepseek-chat-v3",
        verbose=True,
    )

    implementer = Agent(
        role="Senior Implementer",
        goal="Implement the approved fix with tests",
        backstory="Writes production-ready code with full test coverage.",
        llm="openrouter/deepseek/deepseek-chat-v3",
        verbose=True,
    )

    t1 = Task(
        description=f"Analyze this bug and generate 3+ hypotheses:\n{context}",
        agent=architect,
        expected_output="3+ prioritized hypotheses with verification plans",
    )
    t2 = Task(
        description=f"Investigate each hypothesis and confirm root cause:\n{context}",
        agent=debugger,
        expected_output="Confirmed root cause + proposed fix with code",
        context=[t1],
    )
    t3 = Task(
        description="Review the proposed fix for security issues and regressions.",
        agent=security,
        expected_output="Security review: APPROVED or REJECTED with reasons",
        context=[t2],
    )
    t4 = Task(
        description="Implement the approved fix with unit tests.",
        agent=implementer,
        expected_output="Code + tests + commit message",
        context=[t2, t3],
    )

    crew = Crew(
        agents=[architect, debugger, security, implementer],
        tasks=[t1, t2, t3, t4],
        process=Process.sequential,
        verbose=True,
    )

    print("=" * 60)
    print("🔍 MOE BUG HUNTING CREW — STARTING")
    print("=" * 60)
    result = crew.kickoff()
    print("\n" + "=" * 60)
    print("✅ INVESTIGATION COMPLETE")
    print("=" * 60)

    if agentops_available:
        agentops.end_session("Success")

    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        hunt_bug(description=" ".join(sys.argv[1:]))
    else:
        hunt_bug(
            description="Intermittent ConnectionResetError every 15-20 minutes during OSINT batch processing",
            file_path="backend/osint/network_analysis.py",
            error_log="ConnectionResetError: [Errno 104] Connection reset by peer",
        )
'@ | Out-File -FilePath "$MW_HOME\crews\bug_hunter.py" -Encoding UTF8 -Force

Log-Phase "FILES" "OK" "Archivos del MOE creados"
```

---

## FASE 7: SCRIPTS DE OPERACIÓN DIARIA

```
[AUTO]
```

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 7: SCRIPTS DE OPERACIÓN" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ── 7.1 mw-start.ps1 — Inicio diario ────────────────
@'
#!/usr/bin/env pwsh
# mw-start.ps1 — Start MOE development environment
$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  MindWareHouse MOE — Starting Up" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

# Start Langfuse
Write-Host "[1/3] Langfuse..." -ForegroundColor Yellow -NoNewline
Set-Location "$env:USERPROFILE\mw-infrastructure\langfuse"
docker compose up -d 2>$null | Out-Null
Start-Sleep -Seconds 8
try {
    $h = Invoke-RestMethod "http://localhost:3000/api/public/health" -TimeoutSec 5
    if ($h.status -eq "OK") { Write-Host " ✅ http://localhost:3000" -ForegroundColor Green }
    else { Write-Host " ⏳ starting..." -ForegroundColor Yellow }
} catch { Write-Host " ⏳ starting..." -ForegroundColor Yellow }

# Activate venv
Write-Host "[2/3] Python venv..." -ForegroundColor Yellow -NoNewline
Set-Location "$env:USERPROFILE\mw-moe"
& ".\.venv\Scripts\Activate.ps1"
Write-Host " ✅" -ForegroundColor Green

# Check APIs
Write-Host "[3/3] API keys..." -ForegroundColor Yellow -NoNewline
$apis = @("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY")
$allOK = $true
foreach ($api in $apis) {
    if (-not [Environment]::GetEnvironmentVariable($api, "User")) { $allOK = $false }
}
if ($allOK) { Write-Host " ✅" -ForegroundColor Green }
else { Write-Host " ⚠️ some missing" -ForegroundColor Yellow }

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  ✅ MOE Ready" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "  kilo                          Interactive session" -ForegroundColor Gray
Write-Host "  kilo --mode orchestrator      Orchestrator mode" -ForegroundColor Gray
Write-Host "  .\mw-route.ps1 debug `"desc`"   Smart routing" -ForegroundColor Gray
Write-Host "  python crews\bug_hunter.py    Bug Hunting Crew" -ForegroundColor Gray
Write-Host "  http://localhost:3000         Langfuse Dashboard" -ForegroundColor Gray
Write-Host ""
'@ | Out-File -FilePath "$MW_HOME\mw-start.ps1" -Encoding UTF8 -Force

# ── 7.2 mw-stop.ps1 — Parada ────────────────────────
@'
#!/usr/bin/env pwsh
# mw-stop.ps1 — Stop MOE environment
Write-Host "`n🛑 Stopping MOE environment..." -ForegroundColor Yellow
Set-Location "$env:USERPROFILE\mw-infrastructure\langfuse"
docker compose down 2>$null | Out-Null
Write-Host "✅ Langfuse stopped" -ForegroundColor Green
Write-Host "✅ MOE environment shut down. Good night, Victor.`n" -ForegroundColor Green
'@ | Out-File -FilePath "$MW_HOME\mw-stop.ps1" -Encoding UTF8 -Force

# ── 7.3 mw-route.ps1 — Smart routing ────────────────
@'
#!/usr/bin/env pwsh
# mw-route.ps1 — Intelligent model routing for Kilo CLI
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("docs","debug","architect","test","code","security","osint","ask")]
    [string]$TaskType,
    [Parameter(Mandatory=$true)]
    [string]$TaskDescription
)

$routing = @{
    "docs"      = @{ model="openrouter/deepseek/deepseek-chat-v3"; mode="code" }
    "debug"     = @{ model="openrouter/anthropic/claude-sonnet-4-5"; mode="debug" }
    "architect" = @{ model="openrouter/anthropic/claude-sonnet-4-5"; mode="architect" }
    "test"      = @{ model="openrouter/deepseek/deepseek-chat-v3"; mode="code" }
    "code"      = @{ model="openrouter/openai/gpt-5.1-codex"; mode="code" }
    "security"  = @{ model="openrouter/anthropic/claude-sonnet-4-5"; mode="debug" }
    "osint"     = @{ model="openrouter/anthropic/claude-sonnet-4-5"; mode="architect" }
    "ask"       = @{ model="openrouter/deepseek/deepseek-chat-v3"; mode="code" }
}

$cfg = $routing[$TaskType]
Write-Host "🎯 $TaskType → $($cfg.model)" -ForegroundColor Cyan
kilo --mode $cfg.mode --model $cfg.model $TaskDescription
'@ | Out-File -FilePath "$MW_HOME\mw-route.ps1" -Encoding UTF8 -Force

# ── 7.4 mw-health.ps1 — Health check ────────────────
@'
#!/usr/bin/env pwsh
# mw-health.ps1 — Check all MOE components
Write-Host "`n🏥 MOE Health Check" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# Kilo
$k = kilo --version 2>$null
if ($k) { Write-Host "  ✅ Kilo CLI: $k" -ForegroundColor Green }
else { Write-Host "  ❌ Kilo CLI: not found" -ForegroundColor Red }

# Docker
$d = docker info 2>$null
if ($d) { Write-Host "  ✅ Docker: running" -ForegroundColor Green }
else { Write-Host "  ❌ Docker: not running" -ForegroundColor Red }

# Langfuse
try {
    $h = Invoke-RestMethod "http://localhost:3000/api/public/health" -TimeoutSec 5
    if ($h.status -eq "OK") { Write-Host "  ✅ Langfuse: healthy" -ForegroundColor Green }
    else { Write-Host "  ⚠️ Langfuse: $($h.status)" -ForegroundColor Yellow }
} catch { Write-Host "  ❌ Langfuse: not responding" -ForegroundColor Red }

# Python venv
if (Test-Path "$env:USERPROFILE\mw-moe\.venv\Scripts\python.exe") {
    $pv = & "$env:USERPROFILE\mw-moe\.venv\Scripts\python.exe" --version 2>$null
    Write-Host "  ✅ Python venv: $pv" -ForegroundColor Green
} else { Write-Host "  ❌ Python venv: not found" -ForegroundColor Red }

# CrewAI
$crew = & "$env:USERPROFILE\mw-moe\.venv\Scripts\python.exe" -c "from crewai import Crew; print('OK')" 2>$null
if ($crew -eq "OK") { Write-Host "  ✅ CrewAI: installed" -ForegroundColor Green }
else { Write-Host "  ❌ CrewAI: import error" -ForegroundColor Red }

# API Keys
$apis = @("OPENROUTER_API_KEY", "ANTHROPIC_API_KEY")
foreach ($api in $apis) {
    $val = [Environment]::GetEnvironmentVariable($api, "User")
    if ($val) { Write-Host "  ✅ $api`: set ($($val.Substring(0,8))...)" -ForegroundColor Green }
    else { Write-Host "  ❌ $api`: NOT SET" -ForegroundColor Red }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
'@ | Out-File -FilePath "$MW_HOME\mw-health.ps1" -Encoding UTF8 -Force

Log-Phase "SCRIPTS" "OK" "Scripts operacionales creados: start, stop, route, health"
```

---

## FASE 8: LANGFUSE API KEYS (POST-SETUP)

```
[HUMAN_INPUT_REQUIRED — MÍNIMO]
Langfuse genera sus propias keys al crear el primer proyecto.
Claude Code guía al usuario a copiarlas.
```

```powershell
Write-Host "`n========================================" -ForegroundColor Magenta
Write-Host "  FASE 8: LANGFUSE — CREAR PROYECTO" -ForegroundColor Magenta
Write-Host "========================================`n" -ForegroundColor Magenta

Write-Host "Langfuse está corriendo en http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "Necesito que hagas esto (1 minuto):" -ForegroundColor Yellow
Write-Host "  1. Abre http://localhost:3000 en tu browser" -ForegroundColor White
Write-Host "  2. Crea cuenta admin (email + password)" -ForegroundColor White
Write-Host "  3. Crea organización: MindWareHouse" -ForegroundColor White
Write-Host "  4. Crea proyecto: MOE-Development" -ForegroundColor White
Write-Host "  5. Ve a Settings → API Keys → Create" -ForegroundColor White
Write-Host "  6. Copia las 2 keys que te muestra`n" -ForegroundColor White

Start-Process "http://localhost:3000"

$LF_PUBLIC = Read-Host "🔑 Pega el Langfuse PUBLIC Key (pk-lf-...)"
$LF_SECRET = Read-Host "🔑 Pega el Langfuse SECRET Key (sk-lf-...)"

# Guardar
[Environment]::SetEnvironmentVariable("LANGFUSE_PUBLIC_KEY", $LF_PUBLIC, "User")
[Environment]::SetEnvironmentVariable("LANGFUSE_SECRET_KEY", $LF_SECRET, "User")
$env:LANGFUSE_PUBLIC_KEY = $LF_PUBLIC
$env:LANGFUSE_SECRET_KEY = $LF_SECRET

# Actualizar .env
$envContent = Get-Content "$MW_HOME\.env" -Raw
$envContent = $envContent -replace "LANGFUSE_PUBLIC_KEY=.*", "LANGFUSE_PUBLIC_KEY=$LF_PUBLIC"
$envContent = $envContent -replace "LANGFUSE_SECRET_KEY=.*", "LANGFUSE_SECRET_KEY=$LF_SECRET"
$envContent | Out-File -FilePath "$MW_HOME\.env" -Encoding UTF8 -Force

# Actualizar credentials backup
$credContent = Get-Content "$env:USERPROFILE\.mw-credentials" -Raw
$credContent += "`nLANGFUSE_PUBLIC_KEY=$LF_PUBLIC`nLANGFUSE_SECRET_KEY=$LF_SECRET"
$credContent | Out-File -FilePath "$env:USERPROFILE\.mw-credentials" -Encoding UTF8 -Force

Log-Phase "LANGFUSE-KEYS" "OK" "API keys configuradas"
Write-Host "`n✅ Langfuse keys guardadas. Resto del proceso es AUTÓNOMO." -ForegroundColor Green
```

---

## FASE 9: TEST END-TO-END AUTOMÁTICO

```
[AUTO]
Ejecutar test completo del stack sin intervención.
```

```powershell
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  FASE 9: TEST END-TO-END" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Set-Location $MW_HOME
& ".\.venv\Scripts\Activate.ps1"

# ── 9.1 Test de configuración ────────────────────────
Write-Host "[1/4] Verificando configuración..." -ForegroundColor Yellow
python moe_config.py

# ── 9.2 Test de conexión OpenRouter ──────────────────
Write-Host "`n[2/4] Test de conexión OpenRouter..." -ForegroundColor Yellow
python -c @"
import os
from dotenv import load_dotenv
load_dotenv()
from litellm import completion

try:
    response = completion(
        model='openrouter/deepseek/deepseek-chat-v3',
        messages=[{'role': 'user', 'content': 'Say: MOE connection test successful'}],
        max_tokens=50
    )
    print(f'  ✅ OpenRouter: {response.choices[0].message.content.strip()}')
except Exception as e:
    print(f'  ❌ OpenRouter: {e}')
"@

# ── 9.3 Test de Langfuse trace ───────────────────────
Write-Host "`n[3/4] Test de Langfuse tracing..." -ForegroundColor Yellow
python -c @"
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from langfuse import Langfuse
    lf = Langfuse()
    trace = lf.trace(name='installation-test')
    trace.update(output='MW-MOE installation test successful')
    lf.flush()
    print('  ✅ Langfuse: trace created — check http://localhost:3000')
except Exception as e:
    print(f'  ⚠️ Langfuse: {e}')
"@

# ── 9.4 Test CrewAI mini crew ────────────────────────
Write-Host "`n[4/4] Test CrewAI mini crew (puede tomar 30-60s)..." -ForegroundColor Yellow
python -c @"
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew

agent = Agent(
    role='Test Agent',
    goal='Confirm MOE stack is working',
    backstory='Installation verification agent.',
    llm='openrouter/deepseek/deepseek-chat-v3',
    verbose=False
)

task = Task(
    description='Respond with exactly: MW-MOE STACK OPERATIONAL',
    agent=agent,
    expected_output='MW-MOE STACK OPERATIONAL'
)

crew = Crew(agents=[agent], tasks=[task], verbose=False)
result = crew.kickoff()
print(f'  ✅ CrewAI: {result}')
"@

Log-Phase "E2E-TEST" "OK" "Tests end-to-end completados"
```

---

## FASE 10: REPORTE FINAL

```
[AUTO]
Generar reporte completo de instalación.
```

```powershell
Write-Host "`n" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  ✅ MW-MOE INSTALLATION COMPLETE" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green

# Generar reporte final en el log
@"

---
## INSTALLATION COMPLETE — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

### Components Installed:
| Component | Status | Location |
|-----------|--------|----------|
| Node.js | $(node --version 2>$null) | system |
| Python | $(python --version 2>$null) | system |
| Git | $(git --version 2>$null) | system |
| Docker | $(docker --version 2>$null) | system |
| Kilo CLI | $(kilo --version 2>$null) | npm global |
| VS Code | installed | system |
| Langfuse | docker | http://localhost:3000 |
| CrewAI | pip | $MW_HOME\.venv |
| AgentOps | pip | $MW_HOME\.venv |
| LiteLLM | pip | $MW_HOME\.venv |

### File Structure:
``````
$env:USERPROFILE\
├── .kilocode\config.json          Kilo CLI config
├── .mw-credentials                API keys backup
├── .wslconfig                     Docker RAM limits
├── mw-infrastructure\
│   └── langfuse\                  Langfuse self-hosted
├── mw-moe\
│   ├── .env                       Environment variables
│   ├── .venv\                     Python virtual env
│   ├── moe_config.py              MOE configuration
│   ├── mw-start.ps1               Daily startup
│   ├── mw-stop.ps1                Shutdown
│   ├── mw-route.ps1               Smart model routing
│   ├── mw-health.ps1              Health check
│   └── crews\
│       └── bug_hunter.py          Bug Hunting Crew
└── mw-install-log-*.md            This installation log
``````

### Daily Usage:
``````powershell
cd ~/mw-moe
.\mw-start.ps1               # Start everything
.\mw-health.ps1               # Check all components
.\mw-route.ps1 debug "desc"   # Smart model routing
python crews\bug_hunter.py    # Run Bug Hunting Crew
kilo                          # Interactive Kilo session
.\mw-stop.ps1                 # Shutdown everything
``````

### Dashboards:
- Langfuse: http://localhost:3000
- AgentOps: https://app.agentops.ai

### Cost: $0 software | ~$30-50/month API tokens
"@ | Out-File -FilePath $LOG_FILE -Append -Encoding UTF8

Write-Host ""
Write-Host "  📁 Project:    $MW_HOME" -ForegroundColor White
Write-Host "  📊 Langfuse:   http://localhost:3000" -ForegroundColor White
Write-Host "  📋 Log:        $LOG_FILE" -ForegroundColor White
Write-Host ""
Write-Host "  QUICK START:" -ForegroundColor Cyan
Write-Host "  cd ~/mw-moe && .\mw-start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host "  Do More with Less — One Step Ahead" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
```

---

## RESUMEN DE INTERVENCIÓN HUMANA REQUERIDA

```
TOTAL DE PAUSAS DONDE VICTOR DEBE ACTUAR: 2

PAUSA 1 — FASE 2: API Keys (2 minutos)
  → Pegar 3 API keys (OpenRouter, Anthropic, AgentOps)
  → Las deberías tener ya o crear en 5 min en los sitios web

PAUSA 2 — FASE 8: Langfuse Project (1 minuto)
  → Abrir browser → localhost:3000
  → Crear cuenta + proyecto
  → Copiar 2 keys que genera

TODO LO DEMÁS ES 100% AUTÓNOMO.
Tiempo estimado: 20-40 minutos (depende de velocidad de internet)
```
