# 🛠️ INSTRUCTIVO DE INSTALACIÓN COMPLETO
# Entorno de Desarrollo MOE — MindWareHouse
## Basado en Kilo CLI + CrewAI + Langfuse + AgentOps

**Versión:** 1.0  
**Fecha:** Febrero 2026  
**Autor:** Claude (Strategic Coordinator) para Victor Hernandez  
**Sistema Target:** Windows 10/11 (Dell OptiPlex i7-7700 / 32GB RAM actual)  
**Sistema Futuro:** Ryzen 9 7950X / 128GB RAM / RTX 3090

---

## TABLA DE CONTENIDO

1. [Prerequisitos del Sistema](#1-prerequisitos-del-sistema)
2. [Fase 1: Fundación — Node.js, Python, Git, Docker](#2-fase-1-fundación)
3. [Fase 2: Kilo CLI + Kilo VS Code Extension](#3-fase-2-kilo-cli)
4. [Fase 3: OpenRouter — Gateway Universal de Modelos](#4-fase-3-openrouter)
5. [Fase 4: Langfuse — Observabilidad Self-Hosted](#5-fase-4-langfuse)
6. [Fase 5: CrewAI — Orquestación Multi-Agente](#6-fase-5-crewai)
7. [Fase 6: AgentOps — Monitoring + Loop Detection](#7-fase-6-agentops)
8. [Fase 7: Configuración del MOE Integrado](#8-fase-7-configuración-moe)
9. [Fase 8: Primer Test End-to-End](#9-fase-8-primer-test)
10. [Fase 9: Workflows Automatizados](#10-fase-9-workflows)
11. [Troubleshooting](#11-troubleshooting)
12. [Mantenimiento y Actualizaciones](#12-mantenimiento)

---

## 1. PREREQUISITOS DEL SISTEMA

### 1.1 Verificar tu hardware actual

Abre PowerShell como Administrador y ejecuta:

```powershell
# Verificar CPU, RAM y OS
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type" /C:"Total Physical Memory" /C:"Processor"

# Verificar espacio en disco (necesitas mínimo 50GB libres)
Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N="Free(GB)";E={[math]::Round($_.Free/1GB,2)}}, @{N="Used(GB)";E={[math]::Round($_.Used/1GB,2)}}

# Verificar si ya tienes algunas herramientas
node --version 2>$null; if ($?) { Write-Host "✅ Node.js instalado" } else { Write-Host "❌ Node.js NO instalado" }
python --version 2>$null; if ($?) { Write-Host "✅ Python instalado" } else { Write-Host "❌ Python NO instalado" }
git --version 2>$null; if ($?) { Write-Host "✅ Git instalado" } else { Write-Host "❌ Git NO instalado" }
docker --version 2>$null; if ($?) { Write-Host "✅ Docker instalado" } else { Write-Host "❌ Docker NO instalado" }
```

### 1.2 Requisitos mínimos

```
COMPONENTE          │  MÍNIMO           │  TU PC ACTUAL      │  TU WS FUTURO
────────────────────┼───────────────────┼────────────────────┼──────────────────
CPU                 │  4 cores          │  i7-7700 (4c/8t) ✅│  Ryzen 9 (16c) ✅
RAM                 │  16GB             │  32GB ✅           │  128GB ✅
Disco libre         │  50GB             │  Verificar ⚠️      │  2TB ✅
OS                  │  Windows 10+      │  Win 10 Pro ✅     │  Win 11 ✅
Internet            │  Estable          │  Requerido ✅      │  Requerido ✅
```

### 1.3 Cuentas necesarias (crear ANTES de instalar)

Abre el browser y crea estas cuentas gratuitas:

```
1. ☐ OpenRouter    → https://openrouter.ai/keys
                      (Obtener API Key — anotar como OPENROUTER_API_KEY)

2. ☐ Kilo Code     → https://app.kilo.ai
                      (Crear cuenta — se usa para Agent Manager y sync)

3. ☐ Langfuse      → Se instala local (no necesita cuenta cloud)

4. ☐ AgentOps      → https://app.agentops.ai
                      (Crear cuenta gratuita — obtener API Key)

5. ☐ Anthropic     → https://console.anthropic.com
                      (Si aún no tienes API key — ANTHROPIC_API_KEY)

6. ☐ GitHub        → https://github.com
                      (Si no tienes cuenta aún)
```

**IMPORTANTE:** Guarda TODAS las API keys en un archivo seguro:

```powershell
# Crear archivo de credenciales (NO subir a Git jamás)
New-Item -Path "$env:USERPROFILE\.mw-credentials" -ItemType File -Force
notepad "$env:USERPROFILE\.mw-credentials"
```

Pega esto en el archivo y completa:
```
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
AGENTOPS_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
LANGFUSE_HOST=http://localhost:3000
```

---

## 2. FASE 1: FUNDACIÓN

### 2.1 Instalar Node.js (v20 LTS)

```powershell
# Opción A: Descarga directa (más simple)
# Ir a https://nodejs.org → Descargar LTS (v20.x)
# Ejecutar el instalador .msi con defaults

# Opción B: Via winget (si lo tienes)
winget install OpenJS.NodeJS.LTS

# VERIFICAR (cerrar y abrir nueva terminal)
node --version    # Debe mostrar v20.x.x o superior
npm --version     # Debe mostrar 10.x.x o superior
```

**☐ Checkpoint:** `node --version` muestra v20+

### 2.2 Instalar Python 3.12+

```powershell
# Opción A: Descarga directa
# Ir a https://www.python.org/downloads/ → Descargar 3.12.x
# IMPORTANTE: Marcar "Add Python to PATH" durante instalación
# IMPORTANTE: Marcar "Install for all users"

# Opción B: Via winget
winget install Python.Python.3.12

# VERIFICAR (cerrar y abrir nueva terminal)
python --version   # Debe mostrar Python 3.12.x
pip --version      # Debe mostrar pip 24.x
```

**☐ Checkpoint:** `python --version` muestra 3.12+

### 2.3 Instalar Git

```powershell
# Via winget (recomendado)
winget install Git.Git

# O descargar de https://git-scm.com/download/win

# VERIFICAR
git --version     # Debe mostrar git version 2.x

# CONFIGURAR identidad
git config --global user.name "Victor Hernandez"
git config --global user.email "tu-email@ejemplo.com"
git config --global init.defaultBranch main
```

**☐ Checkpoint:** `git --version` funciona

### 2.4 Instalar Docker Desktop

```powershell
# Descargar de https://www.docker.com/products/docker-desktop/
# Ejecutar instalador
# IMPORTANTE: Habilitar WSL 2 backend durante instalación
# Reiniciar PC cuando lo pida

# Después del reinicio, abrir Docker Desktop y esperar que inicie
# Luego en terminal:
docker --version          # Docker version 27.x
docker compose version    # Docker Compose version v2.x

# Test rápido
docker run hello-world
```

**⚠️ NOTA para tu PC actual (32GB RAM):**
Docker Desktop por default consume mucha RAM. Limitarlo:

```powershell
# Crear archivo de configuración WSL
notepad "$env:USERPROFILE\.wslconfig"
```

Pegar esto:
```ini
[wsl2]
memory=8GB
processors=4
swap=4GB
```

```powershell
# Reiniciar WSL para aplicar
wsl --shutdown
```

**☐ Checkpoint:** `docker run hello-world` muestra mensaje de éxito

### 2.5 Instalar VS Code (si no lo tienes)

```powershell
winget install Microsoft.VisualStudioCode

# Extensiones esenciales (ejecutar después de instalar VS Code)
code --install-extension ms-python.python
code --install-extension ms-vscode.powershell
code --install-extension eamodio.gitlens
```

**☐ Checkpoint:** VS Code abre correctamente

---

## 3. FASE 2: KILO CLI + KILO VS CODE EXTENSION

### 3.1 Instalar Kilo CLI

```powershell
# Instalar globalmente via npm
npm install -g @kilocode/cli

# VERIFICAR
kilo --version     # Debe mostrar 1.x.x

# Si npm da error de permisos:
# Opción: configurar npm para instalar globalmente sin admin
npm config set prefix "$env:APPDATA\npm"
# Luego asegurar que $env:APPDATA\npm esté en tu PATH
```

**☐ Checkpoint:** `kilo --version` muestra 1.x.x

### 3.2 Configurar Kilo CLI

```powershell
# Iniciar Kilo por primera vez (abre el TUI)
cd $env:USERPROFILE
kilo

# Dentro del TUI de Kilo:
# 1. Ejecutar /connect
# 2. Agregar OpenRouter como provider:
#    - Provider: openrouter
#    - API Key: (pegar tu OPENROUTER_API_KEY)
#    - Default model: deepseek/deepseek-chat-v3
#
# 3. Agregar Anthropic como provider:
#    - Provider: anthropic
#    - API Key: (pegar tu ANTHROPIC_API_KEY)
#    - Default model: claude-sonnet-4-5-20250929
#
# 4. Salir con /exit
```

### 3.3 Configurar Auto-Approval (para modo autónomo)

```powershell
# Abrir o crear config
notepad "$env:USERPROFILE\.kilocode\config.json"
```

Pegar esta configuración base:

```json
{
  "autoApproval": {
    "enabled": true,
    "read": {
      "enabled": true,
      "outside": false
    },
    "write": {
      "enabled": true,
      "outside": false,
      "protected": false
    },
    "execute": {
      "enabled": true,
      "allowed": ["npm", "git", "pnpm", "python", "pip", "pytest", "node"],
      "denied": ["rm -rf", "sudo", "format", "del /s"]
    },
    "browser": {
      "enabled": false
    },
    "mcp": {
      "enabled": true
    },
    "mode": {
      "enabled": true
    },
    "subtasks": {
      "enabled": true
    }
  }
}
```

**☐ Checkpoint:** `kilo` abre el TUI correctamente

### 3.4 Instalar Kilo Extension para VS Code

```powershell
# Desde terminal
code --install-extension kilocode.Kilo-Code

# O desde VS Code:
# 1. Abrir VS Code
# 2. Ctrl+Shift+X (extensiones)
# 3. Buscar "Kilo Code"
# 4. Instalar
# 5. Click en "Sign In" en la barra lateral de Kilo
# 6. Autenticar con tu cuenta Kilo
```

### 3.5 Configurar Sign-in con OpenAI Codex (opcional pero recomendado)

```
Dentro de VS Code:
1. Abrir panel de Kilo Code (barra lateral izquierda)
2. Settings (⚙️)
3. Providers → Add Provider
4. Seleccionar "OpenAI Codex"
5. Click "Sign in to OpenAI Codex"
6. Autenticar en el browser
7. Listo — acceso a GPT-5.1-Codex sin pay-as-you-go extra
```

**☐ Checkpoint:** Kilo en VS Code muestra panel funcional con tus providers

### 3.6 Probar Kilo CLI funcional

```powershell
# Crear directorio de prueba
mkdir $env:USERPROFILE\kilo-test
cd $env:USERPROFILE\kilo-test
git init

# Probar modo interactivo
kilo

# Dentro de Kilo, escribir:
> Create a simple Python hello world script

# Verificar que crea el archivo
# Salir con /exit

# Probar modo autónomo
kilo --auto --json "Create a Python script that prints the current date and time"

# Probar con modelo específico
kilo --mode architect --model openrouter/anthropic/claude-sonnet-4-5 "Describe the architecture of a REST API"
```

**☐ Checkpoint:** Kilo crea archivos y responde correctamente

---

## 4. FASE 3: OPENROUTER — GATEWAY UNIVERSAL

### 4.1 Verificar API Key

```powershell
# Test rápido de OpenRouter
curl -s https://openrouter.ai/api/v1/models -H "Authorization: Bearer $env:OPENROUTER_API_KEY" | python -m json.tool | Select-Object -First 20

# Si curl no está disponible, usar PowerShell:
$headers = @{ "Authorization" = "Bearer TU_OPENROUTER_API_KEY_AQUI" }
$response = Invoke-RestMethod -Uri "https://openrouter.ai/api/v1/models" -Headers $headers
$response.data | Select-Object -First 5 | Format-Table id, pricing
```

### 4.2 Configurar variables de entorno permanentes

```powershell
# Configurar variables de entorno a nivel de usuario (persistentes)
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-v1-TU-KEY-AQUI", "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-TU-KEY-AQUI", "User")
[Environment]::SetEnvironmentVariable("AGENTOPS_API_KEY", "TU-KEY-AQUI", "User")
[Environment]::SetEnvironmentVariable("LANGFUSE_PUBLIC_KEY", "pk-lf-TU-KEY-AQUI", "User")
[Environment]::SetEnvironmentVariable("LANGFUSE_SECRET_KEY", "sk-lf-TU-KEY-AQUI", "User")
[Environment]::SetEnvironmentVariable("LANGFUSE_HOST", "http://localhost:3000", "User")

# CERRAR Y ABRIR nueva terminal para que tomen efecto

# Verificar
echo $env:OPENROUTER_API_KEY    # Debe mostrar tu key
echo $env:LANGFUSE_HOST         # Debe mostrar http://localhost:3000
```

**☐ Checkpoint:** Todas las variables de entorno configuradas

---

## 5. FASE 4: LANGFUSE — OBSERVABILIDAD SELF-HOSTED

### 5.1 Clonar e iniciar Langfuse

```powershell
# Crear directorio para servicios de infraestructura
mkdir $env:USERPROFILE\mw-infrastructure
cd $env:USERPROFILE\mw-infrastructure

# Clonar Langfuse
git clone https://github.com/langfuse/langfuse.git
cd langfuse

# Iniciar con Docker Compose
docker compose up -d

# Esperar ~60 segundos a que inicie completamente
Start-Sleep -Seconds 60

# Verificar que los contenedores están corriendo
docker compose ps
```

### 5.2 Configurar Langfuse

```
1. Abrir browser → http://localhost:3000
2. Crear cuenta de administrador:
   - Email: victor@mindwarehouse.com (o el que prefieras)
   - Password: (elegir una segura)
3. Crear organización: "MindWareHouse"
4. Crear proyecto: "MOE-Development"
5. Ir a Settings → API Keys
6. Crear nueva API Key
7. COPIAR el Public Key y Secret Key
8. Actualizar tus variables de entorno:
```

```powershell
[Environment]::SetEnvironmentVariable("LANGFUSE_PUBLIC_KEY", "pk-lf-TU-KEY-REAL", "User")
[Environment]::SetEnvironmentVariable("LANGFUSE_SECRET_KEY", "sk-lf-TU-KEY-REAL", "User")
```

### 5.3 Crear script de inicio/parada de Langfuse

```powershell
# Crear script de inicio
@"
# start-langfuse.ps1
Write-Host "🚀 Iniciando Langfuse..." -ForegroundColor Green
Set-Location "$env:USERPROFILE\mw-infrastructure\langfuse"
docker compose up -d
Start-Sleep -Seconds 10
Write-Host "✅ Langfuse disponible en http://localhost:3000" -ForegroundColor Green
Start-Process "http://localhost:3000"
"@ | Out-File -FilePath "$env:USERPROFILE\mw-infrastructure\start-langfuse.ps1" -Encoding UTF8

# Crear script de parada
@"
# stop-langfuse.ps1
Write-Host "🛑 Deteniendo Langfuse..." -ForegroundColor Yellow
Set-Location "$env:USERPROFILE\mw-infrastructure\langfuse"
docker compose down
Write-Host "✅ Langfuse detenido" -ForegroundColor Green
"@ | Out-File -FilePath "$env:USERPROFILE\mw-infrastructure\stop-langfuse.ps1" -Encoding UTF8
```

### 5.4 Optimización de RAM para tu PC actual (32GB)

```powershell
# Langfuse con Docker consume ~2-3GB RAM
# En tu PC actual de 32GB, esto es manejable
# Pero si necesitas liberar RAM:

# Ver uso actual de Docker
docker stats --no-stream

# Si Langfuse usa demasiada RAM, limitar en docker-compose.override.yml:
cd $env:USERPROFILE\mw-infrastructure\langfuse

@"
services:
  langfuse-web:
    deploy:
      resources:
        limits:
          memory: 1G
  langfuse-worker:
    deploy:
      resources:
        limits:
          memory: 512M
"@ | Out-File -FilePath "docker-compose.override.yml" -Encoding UTF8

# Reiniciar con límites
docker compose down
docker compose up -d
```

**☐ Checkpoint:** http://localhost:3000 muestra dashboard de Langfuse

---

## 6. FASE 5: CREWAI — ORQUESTACIÓN MULTI-AGENTE

### 6.1 Crear entorno virtual Python para MOE

```powershell
# Crear directorio del proyecto MOE
mkdir $env:USERPROFILE\mw-moe
cd $env:USERPROFILE\mw-moe

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Si da error de políticas de ejecución:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1

# Verificar que estás en el venv
python --version    # Debe mostrar Python 3.12.x
pip --version       # Debe apuntar al venv
```

### 6.2 Instalar CrewAI y dependencias

```powershell
# Asegurar que el venv está activado
# (debes ver (.venv) al inicio del prompt)

# Instalar CrewAI con extras de Anthropic
pip install crewai[anthropic]

# Instalar LiteLLM para routing multi-modelo
pip install litellm

# Instalar integración Langfuse
pip install langfuse

# Instalar AgentOps
pip install agentops

# Instalar utilidades adicionales
pip install python-dotenv rich

# Verificar instalación
python -c "from crewai import Agent, Task, Crew; print('✅ CrewAI instalado correctamente')"
python -c "from langfuse import Langfuse; print('✅ Langfuse SDK instalado correctamente')"
python -c "import agentops; print('✅ AgentOps instalado correctamente')"
```

### 6.3 Crear archivo .env del proyecto

```powershell
@"
# .env — MindWareHouse MOE Configuration
# ⚠️ NUNCA subir este archivo a Git

# OpenRouter (Gateway universal)
OPENROUTER_API_KEY=sk-or-v1-TU-KEY

# Anthropic (Directo para tareas críticas)
ANTHROPIC_API_KEY=sk-ant-TU-KEY

# Langfuse (Observabilidad)
LANGFUSE_PUBLIC_KEY=pk-lf-TU-KEY
LANGFUSE_SECRET_KEY=sk-lf-TU-KEY
LANGFUSE_HOST=http://localhost:3000

# AgentOps (Monitoring)
AGENTOPS_API_KEY=TU-KEY

# LiteLLM (Configuración de routing)
LITELLM_LOG=DEBUG
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\.env" -Encoding UTF8

# Crear .gitignore
@"
.env
.venv/
__pycache__/
*.pyc
.langfuse/
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\.gitignore" -Encoding UTF8

# Inicializar Git
git init
git add .gitignore
git commit -m "Initial setup: MW-MOE project"
```

**☐ Checkpoint:** `python -c "from crewai import Crew; print('OK')"` funciona

---

## 7. FASE 6: AGENTOPS — MONITORING + LOOP DETECTION

### 7.1 AgentOps ya está instalado (Fase 5)

La integración se activa con 2 líneas en tu código:

```python
import agentops
agentops.init()  # Lee AGENTOPS_API_KEY del .env automáticamente
```

### 7.2 Verificar conexión a AgentOps

```powershell
cd $env:USERPROFILE\mw-moe
.\.venv\Scripts\Activate.ps1

python -c "
import agentops
import os
from dotenv import load_dotenv
load_dotenv()
agentops.init()
print('✅ AgentOps conectado')
print(f'Dashboard: https://app.agentops.ai')
agentops.end_session('Success')
"
```

**☐ Checkpoint:** AgentOps muestra sesión en https://app.agentops.ai

---

## 8. FASE 7: CONFIGURACIÓN DEL MOE INTEGRADO

### 8.1 Crear el archivo principal del MOE

```powershell
cd $env:USERPROFILE\mw-moe
.\.venv\Scripts\Activate.ps1
```

Crear el archivo `moe_config.py`:

```powershell
@"
"""
MindWareHouse MOE Configuration
================================
Configuración central del Mixture of Experts para desarrollo.
Conecta CrewAI + Langfuse + AgentOps + OpenRouter.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================
# MODELO ROUTING TABLE
# Mapeo de roles a modelos óptimos por costo/rendimiento
# ============================================================

MODEL_ROUTING = {
    # Tareas estratégicas (máxima calidad)
    "architect": "openrouter/anthropic/claude-sonnet-4-5",
    "strategic": "openrouter/anthropic/claude-opus-4-5",

    # Tareas de ejecución (balance calidad/costo)
    "debug": "openrouter/anthropic/claude-sonnet-4-5",
    "code": "openrouter/openai/gpt-5.1-codex",
    "security": "openrouter/anthropic/claude-sonnet-4-5",

    # Tareas de volumen (bajo costo)
    "docs": "openrouter/deepseek/deepseek-chat-v3",
    "test": "openrouter/deepseek/deepseek-chat-v3",
    "ask": "openrouter/deepseek/deepseek-chat-v3",

    # Tareas gratuitas
    "simple": "openrouter/minimax/minimax-m2.1",
    "lint": "openrouter/qwen/qwen-2.5-72b-instruct",
}

# ============================================================
# COSTOS APROXIMADOS POR MODELO (USD por 1M tokens)
# ============================================================

MODEL_COSTS = {
    "claude-opus-4-5": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
    "gpt-5.1-codex": {"input": 2.0, "output": 8.0},
    "deepseek-chat-v3": {"input": 0.27, "output": 1.10},
    "minimax-m2.1": {"input": 0.0, "output": 0.0},
    "qwen-2.5-72b": {"input": 0.0, "output": 0.0},
}

# ============================================================
# CREW TEMPLATES
# ============================================================

CREW_TEMPLATES = {
    "bug_hunting": {
        "description": "Investigar y resolver bugs persistentes",
        "agents": ["architect", "debug", "security", "code"],
        "process": "hierarchical",
    },
    "feature_development": {
        "description": "Desarrollar nuevas features end-to-end",
        "agents": ["architect", "code", "test", "docs"],
        "process": "sequential",
    },
    "code_review": {
        "description": "Review de código con múltiples perspectivas",
        "agents": ["architect", "security", "debug"],
        "process": "sequential",
    },
    "osint_analysis": {
        "description": "Análisis de inteligencia OSINT-MW",
        "agents": ["strategic", "architect", "security"],
        "process": "hierarchical",
    },
}

def get_model(role: str) -> str:
    """Obtener modelo óptimo para un rol dado."""
    return MODEL_ROUTING.get(role, MODEL_ROUTING["ask"])

def print_config():
    """Mostrar configuración actual."""
    print("=" * 60)
    print("MindWareHouse MOE Configuration")
    print("=" * 60)
    print(f"\nOpenRouter: {'✅ Configurado' if os.getenv('OPENROUTER_API_KEY') else '❌ Falta API Key'}")
    print(f"Anthropic:  {'✅ Configurado' if os.getenv('ANTHROPIC_API_KEY') else '❌ Falta API Key'}")
    print(f"Langfuse:   {'✅ Configurado' if os.getenv('LANGFUSE_PUBLIC_KEY') else '❌ Falta API Key'}")
    print(f"AgentOps:   {'✅ Configurado' if os.getenv('AGENTOPS_API_KEY') else '❌ Falta API Key'}")
    print(f"\nModelos configurados: {len(MODEL_ROUTING)}")
    print(f"Crew templates: {len(CREW_TEMPLATES)}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\moe_config.py" -Encoding UTF8
```

### 8.2 Crear el Bug Hunting Crew

Crear el archivo `crews/bug_hunter.py`:

```powershell
mkdir $env:USERPROFILE\mw-moe\crews

@"
"""
Bug Hunting Crew — MindWareHouse MOE
=====================================
Crew especializado en investigar y resolver bugs persistentes.
Usa múltiples modelos AI como expertos con roles diferentes.
"""

import os
import agentops
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langfuse.callback import CallbackHandler

load_dotenv()

# Inicializar monitoring
agentops.init()
langfuse_handler = CallbackHandler()


def create_bug_hunting_crew(
    bug_description: str,
    file_path: str = "",
    error_log: str = ""
):
    """
    Crear y ejecutar un crew de bug hunting.

    Args:
        bug_description: Descripción del bug a investigar
        file_path: Archivo donde se cree que está el bug
        error_log: Log del error si está disponible
    """

    # ── AGENTES ──────────────────────────────────────────────

    architect = Agent(
        role="Arquitecto de Software Senior",
        goal="Analizar la arquitectura del código afectado y generar hipótesis sobre la causa raíz del bug",
        backstory="""Eres un arquitecto de software con 30 años de experiencia.
        Tu fortaleza es ver el big picture: dependencias, race conditions,
        problemas de estado, y patrones de diseño rotos. Generas hipótesis
        ordenadas por probabilidad basándote en tu experiencia.""",
        llm="openrouter/anthropic/claude-sonnet-4-5",
        allow_delegation=True,
        verbose=True,
    )

    debugger = Agent(
        role="Debugger Experto",
        goal="Reproducir el bug, confirmar la causa raíz, y proponer un fix específico",
        backstory="""Eres un especialista en debugging que ha resuelto miles de bugs
        en sistemas de producción. Tu método: reproducir, aislar, diagnosticar, fix.
        Nunca propones un fix sin antes confirmar la causa exacta.""",
        llm="openrouter/anthropic/claude-sonnet-4-5",
        allow_delegation=False,
        verbose=True,
    )

    security_reviewer = Agent(
        role="Analista de Seguridad",
        goal="Verificar que el fix propuesto no introduce vulnerabilidades ni regresiones",
        backstory="""Eres un analista de seguridad especializado en code review.
        Revisas cada fix buscando: injection vulnerabilities, race conditions,
        memory leaks, y edge cases que el debugger pudo haber ignorado.""",
        llm="openrouter/deepseek/deepseek-chat-v3",
        allow_delegation=False,
        verbose=True,
    )

    implementer = Agent(
        role="Implementador Senior",
        goal="Implementar el fix aprobado con código limpio y tests completos",
        backstory="""Eres un desarrollador senior que escribe código production-ready.
        Cada fix incluye: el cambio mínimo necesario, tests unitarios,
        tests de integración, y documentación del cambio.""",
        llm="openrouter/openai/gpt-5.1-codex",
        allow_delegation=False,
        verbose=True,
    )

    # ── TAREAS ───────────────────────────────────────────────

    context = f"""
    Bug: {bug_description}
    Archivo: {file_path}
    Error Log: {error_log}
    """

    task_analyze = Task(
        description=f"""
        Analiza el siguiente bug y genera hipótesis sobre su causa raíz.

        {context}

        ENTREGA:
        1. Mínimo 3 hipótesis ordenadas por probabilidad
        2. Para cada hipótesis: qué la causa, dónde mirar, cómo verificarla
        3. Recomendación de qué hipótesis investigar primero
        """,
        agent=architect,
        expected_output="Reporte con 3+ hipótesis priorizadas con plan de verificación",
    )

    task_debug = Task(
        description=f"""
        Basándote en las hipótesis del arquitecto, investiga cada una.

        {context}

        PROCESO:
        1. Toma la hipótesis más probable
        2. Intenta reproducir el error bajo esa hipótesis
        3. Si se confirma: documenta causa exacta y propón fix
        4. Si no: pasa a la siguiente hipótesis
        5. Repite hasta encontrar la causa raíz

        ENTREGA:
        - Causa raíz confirmada con evidencia
        - Fix propuesto con código específico
        - Explicación de por qué este fix resuelve el problema
        """,
        agent=debugger,
        expected_output="Causa raíz confirmada + fix con código",
        context=[task_analyze],
    )

    task_security = Task(
        description="""
        Revisa el fix propuesto por el debugger.

        VERIFICAR:
        1. No introduce vulnerabilidades de seguridad
        2. No crea race conditions nuevas
        3. No tiene memory leaks
        4. Edge cases cubiertos
        5. No rompe funcionalidad existente

        ENTREGA:
        - APROBADO o RECHAZADO (con razones específicas)
        - Lista de edge cases verificados
        - Sugerencias de mejora si las hay
        """,
        agent=security_reviewer,
        expected_output="Reporte de seguridad: aprobado/rechazado con detalles",
        context=[task_debug],
    )

    task_implement = Task(
        description="""
        Implementa el fix aprobado por seguridad.

        ENTREGA:
        1. Código del fix (mínimo cambio necesario)
        2. Tests unitarios para el fix
        3. Tests de regresión
        4. Comentarios en el código explicando el cambio
        5. Resumen del cambio para commit message
        """,
        agent=implementer,
        expected_output="Código + tests + commit message",
        context=[task_debug, task_security],
    )

    # ── CREW ─────────────────────────────────────────────────

    crew = Crew(
        agents=[architect, debugger, security_reviewer, implementer],
        tasks=[task_analyze, task_debug, task_security, task_implement],
        process=Process.sequential,
        verbose=True,
    )

    # ── EJECUTAR ─────────────────────────────────────────────

    print("=" * 60)
    print("🔍 MOE BUG HUNTING CREW — INICIANDO INVESTIGACIÓN")
    print("=" * 60)
    print(f"Bug: {bug_description}")
    print(f"Archivo: {file_path}")
    print("=" * 60)

    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("✅ INVESTIGACIÓN COMPLETADA")
    print("=" * 60)
    print(result)

    # Cerrar monitoring
    agentops.end_session("Success")

    return result


# ── EJECUCIÓN DIRECTA ───────────────────────────────────────

if __name__ == "__main__":
    # Ejemplo de uso
    result = create_bug_hunting_crew(
        bug_description="Error intermitente en network_analysis.py: "
                        "ConnectionResetError aparece cada 15-20 minutos "
                        "durante procesamiento batch de datos OSINT.",
        file_path="backend/osint/network_analysis.py",
        error_log="ConnectionResetError: [Errno 104] Connection reset by peer"
    )
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\crews\bug_hunter.py" -Encoding UTF8
```

**☐ Checkpoint:** `python moe_config.py` muestra todas las configuraciones ✅

---

## 9. FASE 8: PRIMER TEST END-TO-END

### 9.1 Verificar todo el stack

```powershell
cd $env:USERPROFILE\mw-moe
.\.venv\Scripts\Activate.ps1

# Test 1: Verificar configuración
python moe_config.py

# Test 2: Verificar Langfuse está corriendo
curl -s http://localhost:3000/api/public/health | python -m json.tool
# Debe mostrar: {"status": "OK"}

# Test 3: Verificar Kilo CLI
kilo --version

# Test 4: Verificar Docker
docker compose -f $env:USERPROFILE\mw-infrastructure\langfuse\docker-compose.yml ps
```

### 9.2 Test rápido con CrewAI + Langfuse

```powershell
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Task, Crew
from langfuse.callback import CallbackHandler

handler = CallbackHandler()

agent = Agent(
    role='Test Agent',
    goal='Verificar que el MOE funciona correctamente',
    backstory='Agente de prueba para validar la infraestructura.',
    llm='openrouter/deepseek/deepseek-chat-v3',
    verbose=True
)

task = Task(
    description='Responde: Qué es MindWareHouse? (respuesta breve)',
    agent=agent,
    expected_output='Una descripción breve de MindWareHouse'
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)
result = crew.kickoff()
print('\n✅ TEST EXITOSO')
print(f'Resultado: {result}')
print(f'📊 Ver trace en: http://localhost:3000')
"
```

### 9.3 Verificar trace en Langfuse

```
1. Abrir http://localhost:3000
2. Ir a Tracing → Traces
3. Deberías ver el trace del test
4. Click en el trace para ver:
   - Input/Output del agente
   - Tokens usados
   - Costo estimado
   - Latencia
```

**☐ Checkpoint:** Trace visible en Langfuse dashboard

### 9.4 Test completo con Bug Hunting Crew

```powershell
cd $env:USERPROFILE\mw-moe
.\.venv\Scripts\Activate.ps1

# Ejecutar el Bug Hunting Crew con un caso de prueba
python crews/bug_hunter.py

# Esto va a:
# 1. Iniciar 4 agentes con modelos diferentes
# 2. Reportar cada paso a Langfuse
# 3. Registrar sesión en AgentOps
# 4. Mostrar progreso en tiempo real en terminal
# 5. Tomar ~5-15 minutos dependiendo de la complejidad
```

**☐ Checkpoint:** Bug Hunting Crew completa y traces visibles en Langfuse + AgentOps

---

## 10. FASE 9: WORKFLOWS AUTOMATIZADOS

### 10.1 Script de routing rápido para Kilo CLI

```powershell
# Crear script de routing inteligente
@"
#!/usr/bin/env pwsh
# mw-route.ps1 — Smart Model Routing para Kilo CLI
# Uso: .\mw-route.ps1 <tipo> "<descripción de la tarea>"

param(
    [Parameter(Mandatory=`$true)]
    [ValidateSet("docs","debug","architect","test","code","security","osint","ask")]
    [string]`$TaskType,

    [Parameter(Mandatory=`$true)]
    [string]`$TaskDescription
)

`$routing = @{
    "docs"      = @{ model = "openrouter/deepseek/deepseek-chat-v3"; mode = "code" }
    "debug"     = @{ model = "openrouter/anthropic/claude-sonnet-4-5"; mode = "debug" }
    "architect" = @{ model = "openrouter/anthropic/claude-sonnet-4-5"; mode = "architect" }
    "test"      = @{ model = "openrouter/deepseek/deepseek-chat-v3"; mode = "code" }
    "code"      = @{ model = "openrouter/openai/gpt-5.1-codex"; mode = "code" }
    "security"  = @{ model = "openrouter/anthropic/claude-sonnet-4-5"; mode = "debug" }
    "osint"     = @{ model = "openrouter/anthropic/claude-sonnet-4-5"; mode = "architect" }
    "ask"       = @{ model = "openrouter/deepseek/deepseek-chat-v3"; mode = "code" }
}

`$config = `$routing[`$TaskType]
Write-Host "🎯 Routing: `$TaskType → `$(`$config.model) (`$(`$config.mode) mode)" -ForegroundColor Cyan
kilo --mode `$config.mode --model `$config.model `$TaskDescription
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\mw-route.ps1" -Encoding UTF8
```

**Uso:**
```powershell
.\mw-route.ps1 debug "Fix the ConnectionResetError in network_analysis.py"
.\mw-route.ps1 docs "Update the OSINT-MW API documentation"
.\mw-route.ps1 test "Write unit tests for the data pipeline"  # Modelo barato
.\mw-route.ps1 architect "Design the new intelligence correlation engine"
```

### 10.2 Script de inicio diario

```powershell
@"
#!/usr/bin/env pwsh
# mw-start.ps1 — Iniciar entorno de desarrollo MOE completo

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  MindWareHouse MOE — Iniciando entorno" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# 1. Iniciar Langfuse
Write-Host "`n[1/4] Iniciando Langfuse..." -ForegroundColor Yellow
Set-Location "`$env:USERPROFILE\mw-infrastructure\langfuse"
docker compose up -d 2>`$null
Start-Sleep -Seconds 5
`$health = Invoke-RestMethod -Uri "http://localhost:3000/api/public/health" -ErrorAction SilentlyContinue
if (`$health.status -eq "OK") {
    Write-Host "  ✅ Langfuse: http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Langfuse iniciando... espera 30 segundos" -ForegroundColor Yellow
}

# 2. Activar venv Python
Write-Host "`n[2/4] Activando entorno Python..." -ForegroundColor Yellow
Set-Location "`$env:USERPROFILE\mw-moe"
& ".\.venv\Scripts\Activate.ps1"
Write-Host "  ✅ Python venv activado" -ForegroundColor Green

# 3. Verificar APIs
Write-Host "`n[3/4] Verificando API keys..." -ForegroundColor Yellow
if (`$env:OPENROUTER_API_KEY) { Write-Host "  ✅ OpenRouter" -ForegroundColor Green }
else { Write-Host "  ❌ OpenRouter — falta API key" -ForegroundColor Red }
if (`$env:ANTHROPIC_API_KEY) { Write-Host "  ✅ Anthropic" -ForegroundColor Green }
else { Write-Host "  ❌ Anthropic — falta API key" -ForegroundColor Red }
if (`$env:AGENTOPS_API_KEY) { Write-Host "  ✅ AgentOps" -ForegroundColor Green }
else { Write-Host "  ❌ AgentOps — falta API key" -ForegroundColor Red }

# 4. Mostrar status
Write-Host "`n[4/4] Verificando Kilo CLI..." -ForegroundColor Yellow
`$kiloVersion = kilo --version 2>`$null
if (`$kiloVersion) { Write-Host "  ✅ Kilo CLI: `$kiloVersion" -ForegroundColor Green }
else { Write-Host "  ❌ Kilo CLI no encontrado" -ForegroundColor Red }

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  ✅ Entorno MOE listo para trabajar" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nComandos disponibles:" -ForegroundColor White
Write-Host "  kilo                    → Sesión interactiva Kilo" -ForegroundColor Gray
Write-Host "  kilo --mode orchestrator → Modo orquestador" -ForegroundColor Gray
Write-Host "  .\mw-route.ps1 <tipo> <desc> → Routing inteligente" -ForegroundColor Gray
Write-Host "  python crews\bug_hunter.py   → Bug Hunting Crew" -ForegroundColor Gray
Write-Host "  http://localhost:3000        → Langfuse Dashboard" -ForegroundColor Gray
Write-Host "  https://app.agentops.ai      → AgentOps Dashboard" -ForegroundColor Gray
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\mw-start.ps1" -Encoding UTF8
```

### 10.3 Script de parada nocturna

```powershell
@"
#!/usr/bin/env pwsh
# mw-stop.ps1 — Detener entorno MOE y liberar recursos

Write-Host "🛑 Deteniendo entorno MOE..." -ForegroundColor Yellow

# Detener Langfuse
Set-Location "`$env:USERPROFILE\mw-infrastructure\langfuse"
docker compose down 2>`$null
Write-Host "  ✅ Langfuse detenido" -ForegroundColor Green

# Mostrar resumen de Docker
`$containers = docker ps -q 2>`$null
if (`$containers) {
    Write-Host "  ⚠️ Aún hay contenedores corriendo:" -ForegroundColor Yellow
    docker ps --format "table {{.Names}}\t{{.Status}}"
} else {
    Write-Host "  ✅ No hay contenedores activos" -ForegroundColor Green
}

Write-Host "`n✅ Entorno MOE detenido. Buenas noches, Victor." -ForegroundColor Green
"@ | Out-File -FilePath "$env:USERPROFILE\mw-moe\mw-stop.ps1" -Encoding UTF8
```

---

## 11. TROUBLESHOOTING

### Problema: "kilo" no se reconoce como comando

```powershell
# Verificar que npm global bin está en PATH
npm config get prefix
# Agregar esa ruta al PATH si no está:
$npmPath = npm config get prefix
[Environment]::SetEnvironmentVariable("PATH", "$env:PATH;$npmPath", "User")
# Reiniciar terminal
```

### Problema: Docker Compose no inicia Langfuse

```powershell
# Verificar que Docker Desktop está corriendo
docker info

# Si falla, abrir Docker Desktop y esperar
# Luego reintentar:
cd $env:USERPROFILE\mw-infrastructure\langfuse
docker compose down -v  # Limpiar volúmenes
docker compose up -d    # Reiniciar limpio
```

### Problema: CrewAI no encuentra modelo via OpenRouter

```powershell
# Verificar que el modelo existe en OpenRouter
python -c "
import os
from litellm import completion
os.environ['OPENROUTER_API_KEY'] = os.getenv('OPENROUTER_API_KEY')
response = completion(
    model='openrouter/deepseek/deepseek-chat-v3',
    messages=[{'role': 'user', 'content': 'Say hello'}]
)
print(response.choices[0].message.content)
"
```

### Problema: RAM insuficiente (PC actual 32GB)

```
Prioridad de servicios por RAM:
1. VS Code + Kilo Extension:  ~2GB
2. Langfuse (Docker):         ~2-3GB
3. Python venv + CrewAI:      ~1-2GB
4. Docker Engine:             ~1-2GB
5. Windows OS:                ~4-6GB
─────────────────────────────────────
Total estimado:               ~12-15GB de 32GB

✅ Tu PC actual PUEDE correr todo esto.
Si necesitas liberar RAM: cerrar browsers tabs innecesarios.
```

### Problema: Kilo + VS Code Agent Manager no sincroniza

```
1. Verificar que estás logueado en Kilo Extension (VS Code)
2. Verificar que kilo CLI está logueado: kilo → /connect
3. Si usas BYOK (tus propias API keys), Agent Manager cloud sync
   NO funciona — es limitación conocida de Kilo
4. Workaround: usar sesiones locales (funcionan siempre)
```

---

## 12. MANTENIMIENTO Y ACTUALIZACIONES

### Actualizar componentes (ejecutar mensualmente)

```powershell
# Actualizar Kilo CLI
npm update -g @kilocode/cli

# Actualizar paquetes Python
cd $env:USERPROFILE\mw-moe
.\.venv\Scripts\Activate.ps1
pip install --upgrade crewai litellm langfuse agentops

# Actualizar Langfuse
cd $env:USERPROFILE\mw-infrastructure\langfuse
git pull
docker compose down
docker compose up -d

# Actualizar Kilo VS Code Extension
code --install-extension kilocode.Kilo-Code --force
```

### Backup de configuración

```powershell
# Backup semanal de configs
$backupDir = "$env:USERPROFILE\mw-backups\$(Get-Date -Format 'yyyy-MM-dd')"
mkdir $backupDir -Force
Copy-Item "$env:USERPROFILE\.kilocode\config.json" "$backupDir\" -Force
Copy-Item "$env:USERPROFILE\mw-moe\.env" "$backupDir\" -Force
Copy-Item "$env:USERPROFILE\.mw-credentials" "$backupDir\" -Force
Write-Host "✅ Backup guardado en $backupDir"
```

---

## RESUMEN: ESTRUCTURA FINAL DE ARCHIVOS

```
C:\Users\Victor\
├── .kilocode\
│   └── config.json              ← Configuración de Kilo CLI
├── .mw-credentials              ← API Keys (NUNCA en Git)
├── mw-infrastructure\
│   └── langfuse\                ← Langfuse self-hosted
│       ├── docker-compose.yml
│       └── docker-compose.override.yml
├── mw-moe\
│   ├── .env                     ← Variables de entorno del proyecto
│   ├── .gitignore
│   ├── .venv\                   ← Entorno virtual Python
│   ├── moe_config.py            ← Configuración central del MOE
│   ├── mw-route.ps1             ← Script de routing para Kilo
│   ├── mw-start.ps1             ← Script de inicio diario
│   ├── mw-stop.ps1              ← Script de parada
│   └── crews\
│       └── bug_hunter.py        ← Bug Hunting Crew
└── mw-backups\                  ← Backups semanales
```

---

## CHECKLIST FINAL DE VERIFICACIÓN

```
FASE 1: FUNDACIÓN
  ☐ Node.js v20+ instalado y funcional
  ☐ Python 3.12+ instalado con pip
  ☐ Git configurado con identidad
  ☐ Docker Desktop corriendo
  ☐ VS Code con extensiones base

FASE 2: KILO CLI
  ☐ kilo --version muestra 1.x.x
  ☐ Providers configurados (OpenRouter + Anthropic)
  ☐ Auto-approval configurado
  ☐ Kilo Extension en VS Code funcional
  ☐ OpenAI Codex sign-in completado (opcional)

FASE 3: OPENROUTER
  ☐ API Key válida y testeada
  ☐ Variables de entorno permanentes configuradas

FASE 4: LANGFUSE
  ☐ Docker containers corriendo
  ☐ Dashboard accesible en http://localhost:3000
  ☐ Proyecto creado con API keys

FASE 5: CREWAI
  ☐ Entorno virtual Python creado y activado
  ☐ crewai, langfuse, agentops instalados
  ☐ Archivo .env configurado

FASE 6: AGENTOPS
  ☐ Conexión verificada
  ☐ Sesión visible en dashboard

FASE 7: CONFIGURACIÓN MOE
  ☐ moe_config.py muestra todo ✅
  ☐ Bug Hunting Crew creado

FASE 8: TEST END-TO-END
  ☐ Test rápido de CrewAI ejecutado
  ☐ Trace visible en Langfuse
  ☐ Sesión visible en AgentOps
  ☐ Bug Hunting Crew completó ejecución

FASE 9: WORKFLOWS
  ☐ mw-route.ps1 funciona
  ☐ mw-start.ps1 inicia todo correctamente
  ☐ mw-stop.ps1 detiene todo limpiamente
```

---

**Tiempo estimado de instalación completa: 2-4 horas**  
**Costo de software: $0 (todo open source o free tier)**  
**Costo operativo mensual estimado: $30-50 (tokens API)**

*"Do More with Less" — Un ecosistema completo de desarrollo AI*
*por el precio de una suscripción de streaming.*
