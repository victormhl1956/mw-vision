# MW-VISION: EL CENTRO DE COMANDO VISUAL
## "Porque un arquitecto no construye a ciegas"

### MindWareHouse — Victor Hernandez
### Arquitectura Completa v1.0

---

## EL PROBLEMA: ESTÁS ORQUESTANDO UNA SINFONÍA CON LOS OJOS CERRADOS

Victor, lo que describes no es un problema de herramientas. Es un problema de **visibilidad**. Hoy tienes:

- Un MOE con 6+ modelos ruteando tareas → **no ves el flujo**
- Agentes CrewAI ejecutando misiones → **no ves su progreso**
- Hydra fragmentando código → **no ves la descomposición**
- Un pipeline que genera resultados → **no ves hasta que termina**
- Un stack que cuesta $5-45/mes → **no ves dónde se gasta**

Las IDEs (VS Code, Cursor, etc.) están diseñadas para **escribir** código. Tú necesitas **dirigir** un sistema. Necesitas lo que un director de orquesta tiene: **la partitura completa en vista, cada músico visible, y la batuta en la mano.**

---

## LA SOLUCIÓN: MW-VISION

Una app de escritorio Windows nativa + acceso remoto desde móvil que te da **4 vistas**:

```
┌─────────────────────────────────────────────────────────┐
│                    MW-VISION                             │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │🔀 FLOW   │ │👥 TEAM   │ │💬 CHAT   │ │🏗️ BLUEPRINT│  │
│  │          │ │          │ │          │ │           │   │
│  │ Ver cómo │ │ Ver quién│ │ Hablar   │ │ Ver la    │   │
│  │ fluye la │ │ trabaja  │ │ con el   │ │ maqueta   │   │
│  │ data     │ │ en qué   │ │ sistema  │ │ completa  │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│                                                          │
│  [System Tray] ← Corre en background mientras trabajas   │
│  [Mobile PWA] ← Controla desde el teléfono               │
└─────────────────────────────────────────────────────────┘
```

---

## STACK TÉCNICO

### ¿Por qué esta combinación?

| Componente | Tecnología | Razón |
|---|---|---|
| **Desktop Shell** | **Tauri 2.0** (Rust) | 50% menos RAM que Electron. ~2-3MB vs 150MB+. Perfecto para Dell 32GB. Usa WebView2 nativo de Windows, no empaqueta un browser. (GitHub: tauri-apps/tauri — 90k+ stars) |
| **Frontend UI** | **React + TypeScript** | Ecosistema masivo. React Flow para nodos visuales. shadcn/ui para componentes pro. Tailwind para styling rápido. |
| **Visualización de Flujo** | **React Flow** (xyflow) | La librería #1 para UIs basadas en nodos. Usada por Stripe, Typeform. Drag-and-drop, zoom, pan, custom nodes. Perfecta para visualizar MOE routing. (reactflow.dev — 30k+ stars) |
| **Backend/Motor** | **FastAPI** (Python) | Tu stack MOE ya es Python. FastAPI soporta WebSockets nativos para real-time. Se empaqueta como sidecar de Tauri vía PyInstaller. Template oficial existe: tauri-fastapi-full-stack-template |
| **Real-time** | **WebSockets** | Comunicación bidireccional persistente. El backend emite eventos conforme los agentes trabajan. El frontend se actualiza automáticamente. Tauri tiene plugin oficial de WebSocket. |
| **Estado** | **Zustand** | Gestión de estado minimalista para React. 1KB. Sin boilerplate. React Flow lo recomienda oficialmente para su AI Workflow Editor template. |
| **Charts/Métricas** | **Recharts** | Gráficos React declarativos sobre D3. Actualización 3.0 en 2025 con mejor TypeScript. Ligero, perfecto para dashboards de costos. |
| **Base de datos local** | **SQLite** (via SQLModel) | Sin servidor. Un archivo. Persiste historial de tareas, métricas, logs. SQLModel es del creador de FastAPI (Sebastián Ramírez). |
| **Acceso remoto** | **Tailscale + PWA** | Tailscale: VPN mesh peer-to-peer, zero-config. PWA: El mismo frontend React sirve como app instalable en el móvil. Sin publicar nada a internet. |

### Arquitectura Completa

```
┌─────────────────────────────────────────────────────────────┐
│                        TU TELÉFONO                           │
│                    (durante delivery)                         │
│                                                               │
│    ┌──────────────────────────────┐                          │
│    │     PWA (React mismo UI)     │                          │
│    │     ↕ Tailscale VPN          │                          │
│    └──────────────┬───────────────┘                          │
│                   │                                           │
└───────────────────┼───────────────────────────────────────────┘
                    │ WebSocket (wss://)
                    │
┌───────────────────┼───────────────────────────────────────────┐
│                DELL OPTIPLEX (tu PC)                           │
│                                                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              TAURI 2.0 SHELL (Rust)                     │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │           REACT FRONTEND (WebView2)               │   │   │
│  │  │                                                    │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────┐ ┌───────────┐  │   │   │
│  │  │  │ FLOW    │ │ TEAM    │ │CHAT │ │ BLUEPRINT │  │   │   │
│  │  │  │ VIEW    │ │ VIEW    │ │     │ │           │  │   │   │
│  │  │  │         │ │         │ │     │ │           │  │   │   │
│  │  │  │ReactFlow│ │Agents   │ │Input│ │Arch.Diag. │  │   │   │
│  │  │  │Nodes    │ │Cards    │ │Box  │ │ReactFlow  │  │   │   │
│  │  │  └─────────┘ └─────────┘ └─────┘ └───────────┘  │   │   │
│  │  │         ↕ WebSocket (localhost:8765)               │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │        FASTAPI BACKEND (Python sidecar)           │   │   │
│  │  │                                                    │   │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │   │   │
│  │  │  │WebSocket │ │ Task     │ │  MOE Engine       │  │   │   │
│  │  │  │Manager   │ │ Queue    │ │  (tu stack actual)│  │   │   │
│  │  │  └──────────┘ └──────────┘ └──────────────────┘  │   │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │   │   │
│  │  │  │Hydra     │ │ CrewAI   │ │  Ollama          │  │   │   │
│  │  │  │Pipeline  │ │ Crews    │ │  Interface        │  │   │   │
│  │  │  └──────────┘ └──────────┘ └──────────────────┘  │   │   │
│  │  │       ↕ SQLite (mw-vision.db)                     │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  SERVICIOS EXTERNOS                                       │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────────┐  │ │
│  │  │DeepSeek │ │ Qwen    │ │Claude   │ │ Ollama Local  │  │ │
│  │  │  API    │ │  API    │ │  API    │ │ (localhost)   │  │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## LAS 4 VISTAS EN DETALLE

---

### 🔀 VISTA 1: FLOW VIEW — "Ver cómo fluye la información"

**Lo que ves:** Un diagrama de nodos vivo, estilo ComfyUI o n8n, donde cada nodo es un paso en tu pipeline y las conexiones muestran el flujo de datos en tiempo real.

```
┌─────────────────────────────────────────────────────────────┐
│  🔀 FLOW VIEW                                    [⚙️] [📱]  │
│                                                               │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐           │
│  │ 📥 INPUT │─────→│🔀 ROUTER │─────→│🧠 DECOMP │           │
│  │          │      │ (MOE)    │  ┌──→│ (Hydra)  │           │
│  │ "Fix bug │      │          │  │   │          │           │
│  │  in auth"│      │Trust: L2 │  │   │ 5 frags  │           │
│  └──────────┘      └────┬─────┘  │   └────┬─────┘           │
│                         │        │        │                   │
│                    ┌────┴────┐   │   ┌────┴─────────┐        │
│                    │ COST:   │   │   │  FRAGMENTS:   │        │
│                    │ $0.003  │   │   │              │        │
│                    └─────────┘   │   │ ┌──┐┌──┐┌──┐│        │
│                                  │   │ │F1││F2││F3│ │        │
│         ┌────────────────────┐   │   │ │▓▓││▓░││░░│ │        │
│         │  🤖 WORKER POOL    │   │   │ └──┘└──┘└──┘│        │
│         │                    │◄──┘   │ ┌──┐┌──┐    │        │
│         │ DeepSeek → F1 [✅] │       │ │F4││F5│    │        │
│         │ Qwen     → F2 [⏳] │       │ │░░││░░│    │        │
│         │ DeepSeek → F3 [⏳] │       │ └──┘└──┘    │        │
│         │ Ollama   → F4 [🔒] │       └─────────────┘        │
│         │ Ollama   → F5 [🔒] │                               │
│         └────────┬───────────┘       ┌──────────┐           │
│                  │                   │🔧 ASSEMB │           │
│                  └──────────────────→│ (Ollama) │           │
│                                      │          │           │
│                                      │ Status:  │           │
│                                      │ Waiting  │           │
│                                      └────┬─────┘           │
│                                           │                  │
│                                      ┌────┴─────┐           │
│                                      │ 📤 OUTPUT│           │
│                                      │          │           │
│                                      │ auth.py  │           │
│                                      │ (merged) │           │
│                                      └──────────┘           │
│                                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│  📊 Pipeline: 3/5 fragments complete │ Cost: $0.008          │
│  ⏱️ Elapsed: 34s │ Est. remaining: 22s │ Trust: Level 2      │
│  🔒 Hydra: 60% obfuscated │ Exposure: 0% IP at risk         │
└─────────────────────────────────────────────────────────────┘
```

**Tecnología:** React Flow con custom nodes. Cada nodo es un componente React con:
- Color por estado: verde (completo), amarillo (trabajando), gris (esperando), rojo (error)
- Bordes animados mostrando datos fluyendo entre nodos (animated edges)
- Click en cualquier nodo → panel lateral con detalles, logs, payload
- Zoom in/out para ver pipeline completo o detalle de un nodo

**React Flow hace esto posible porque:**
- Los nodos son componentes React customizables con HTML/CSS completo dentro
- Los edges (conexiones) soportan animaciones SVG para mostrar flujo
- Zoom, pan, minimap integrados
- Usado por Stripe y Typeform para exactamente este tipo de UI

---

### 👥 VISTA 2: TEAM VIEW — "Ver al equipo MOE trabajando"

**Lo que ves:** Cada modelo/agente como una "tarjeta de empleado" con status en tiempo real. Como un tablero Kanban pero para agentes AI.

```
┌─────────────────────────────────────────────────────────────┐
│  👥 TEAM VIEW                                    [⚙️] [📱]  │
│                                                               │
│  ┌─── TRABAJANDO ──────────────────────────────────────────┐ │
│  │                                                          │ │
│  │ ┌──────────────────┐  ┌──────────────────┐              │ │
│  │ │ 🟢 DeepSeek V3   │  │ 🟡 Qwen 2.5     │              │ │
│  │ │                   │  │                   │              │ │
│  │ │ Task: Fragment #1 │  │ Task: Fragment #2 │              │ │
│  │ │ "validate_string" │  │ "hash_with_salt"  │              │ │
│  │ │                   │  │                   │              │ │
│  │ │ ⏱️ 12s elapsed    │  │ ⏱️ 8s elapsed     │              │ │
│  │ │ 💰 $0.0003        │  │ 💰 $0.0002        │              │ │
│  │ │ 🔒 Trust: LOW     │  │ 🔒 Trust: LOW     │              │ │
│  │ │ 📊 Tokens: 340/1K │  │ 📊 Tokens: 210/1K │              │ │
│  │ │                   │  │                   │              │ │
│  │ │ [View Prompt]     │  │ [View Prompt]     │              │ │
│  │ │ [View Response]   │  │ [View Response]   │              │ │
│  │ │ [Cancel] [Retry]  │  │ [Cancel] [Retry]  │              │ │
│  │ └──────────────────┘  └──────────────────┘              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─── DISPONIBLES ─────────────────────────────────────────┐ │
│  │                                                          │ │
│  │ ┌──────────────────┐  ┌──────────────────┐              │ │
│  │ │ ⚪ Claude Sonnet  │  │ ⚪ Ollama Local   │              │ │
│  │ │                   │  │ qwen2.5-coder:14b│              │ │
│  │ │ Role: Assembler   │  │ Role: Assembler   │              │ │
│  │ │ Waiting for frags │  │ GPU: 78% free     │              │ │
│  │ │ 💰 $15/1M tokens  │  │ 💰 $0 (local)     │              │ │
│  │ │ 🔒 Trust: HIGH    │  │ 🔒 Trust: MAX     │              │ │
│  │ │ 📊 Today: $2.30   │  │ 📊 Today: 847 tok │              │ │
│  │ │                   │  │                   │              │ │
│  │ │ [Assign Task]     │  │ [Assign Task]     │              │ │
│  │ └──────────────────┘  └──────────────────┘              │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ┌─── HISTORIAL HOY ───────────────────────────────────────┐ │
│  │ 14 tareas completadas │ $0.42 gastados │ 0 errores      │ │
│  │ ████████████████████░░░░░░ 70% del budget diario        │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Interacción con los agentes:**
- Click en un agente → ver su prompt actual, su respuesta parcial (streaming)
- Botón **[Assign Task]** → drag-and-drop una tarea al agente
- Botón **[Cancel]** → abortar tarea actual
- Botón **[Retry]** → re-ejecutar con mismo prompt o editado
- **Chat contextual**: click "Talk to DeepSeek" → abre chat directo con ese modelo específico sobre ESA tarea

---

### 💬 VISTA 3: CHAT VIEW — "Hablar con el sistema"

**Lo que ves:** Un chat inteligente que es tu interfaz de comandos natural. No es un chatbot genérico — es el **puente de mando** de tu sistema.

```
┌─────────────────────────────────────────────────────────────┐
│  💬 COMMAND CHAT                                 [⚙️] [📱]  │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐│
│  │                                                          ││
│  │  🧑 Victor (6:02 AM - before leaving for delivery):      ││
│  │  "Run OSINT crew on target list batch-7. Hydra level 4.  ││
│  │   Report results when done. Priority: HIGH."             ││
│  │                                                          ││
│  │  🤖 MW-VISION (6:02 AM):                                 ││
│  │  "Understood. Starting OSINT Crew with Hydra L4 on       ││
│  │   batch-7 (23 targets). Estimated completion: 2h 15m.    ││
│  │   I'll have results ready by ~8:17 AM.                   ││
│  │                                                          ││
│  │   📋 Plan:                                                ││
│  │   → Decompose into 46 fragments (L4 max granularity)     ││
│  │   → Route: 38 to DeepSeek (boilerplate), 8 to Ollama    ││
│  │   → Assemble locally (Ollama, week rotation = local)     ││
│  │   → Estimated cost: $0.12                                ││
│  │                                                          ││
│  │   Shall I proceed?"                                       ││
│  │                                                          ││
│  │  🧑 Victor: "Go."                                        ││
│  │                                                          ││
│  │  🤖 MW-VISION (6:03 AM):                                 ││
│  │  "✅ Pipeline launched. Tracking in Flow View.             ││
│  │   I'll ping your phone when done or if errors occur."    ││
│  │                                                          ││
│  │  ─── 2 hours later ───                                    ││
│  │                                                          ││
│  │  🤖 MW-VISION (8:14 AM) [📱 PUSH NOTIFICATION]:          ││
│  │  "✅ Batch-7 complete. 23/23 targets processed.           ││
│  │   3 new connections found in network graph.               ││
│  │   Cost: $0.11. Zero IP exposure (Hydra L4).              ││
│  │   Results at: /output/osint/batch-7/report.md             ││
│  │                                                          ││
│  │   ⚠️ 2 targets had unusual patterns — flagged for        ││
│  │   manual review. Want me to open them?"                   ││
│  │                                                          ││
│  └──────────────────────────────────────────────────────────┘│
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ 💬 Type command or question...                    [Send] ││
│  │                                                          ││
│  │ Quick: [Run Crew] [Check Status] [Show Costs] [Stop All]││
│  └──────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**Comandos naturales que entiende:**
- `"Run the OSINT crew on batch-7"` → Lanza crew automáticamente
- `"How much have I spent today?"` → Muestra resumen de costos
- `"What's DeepSeek working on?"` → Status del agente
- `"Stop everything"` → Kill all running pipelines
- `"Show me the auth module architecture"` → Cambia a Blueprint View
- `"Schedule nightly OSINT run at 11pm"` → Crea cron job

---

### 🏗️ VISTA 4: BLUEPRINT VIEW — "La maqueta arquitectónica"

**Lo que ves:** El diagrama arquitectónico completo de tu sistema — como los planos de un edificio. No el flujo de UNA tarea, sino la ESTRUCTURA del edificio entero.

```
┌─────────────────────────────────────────────────────────────┐
│  🏗️ BLUEPRINT VIEW                              [⚙️] [📱]  │
│                                                               │
│  Zoom: [System] [Module] [Function]    Filter: [All] [OSINT]│
│                                                               │
│  ┌──── SYSTEM LEVEL ───────────────────────────────────────┐ │
│  │                                                          │ │
│  │          ┌─────────────────────┐                         │ │
│  │          │   🏢 MW-MOE         │                         │ │
│  │          │   (Orchestrator)    │                         │ │
│  │          └────────┬────────────┘                         │ │
│  │                   │                                      │ │
│  │     ┌─────────────┼─────────────┐                        │ │
│  │     │             │             │                        │ │
│  │  ┌──┴───┐    ┌────┴────┐   ┌───┴────┐                   │ │
│  │  │🐍    │    │🔒       │   │🔍      │                   │ │
│  │  │HYDRA │    │AUTH     │   │OSINT-MW│                   │ │
│  │  │      │    │MODULE   │   │        │                   │ │
│  │  │4 lyrs│    │JWT+2FA  │   │6 crews │                   │ │
│  │  │      │    │         │   │        │                   │ │
│  │  └──┬───┘    └────┬────┘   └───┬────┘                   │ │
│  │     │             │            │                         │ │
│  │  ┌──┴──────────┐  │    ┌───────┴──────────┐              │ │
│  │  │ Decomposer  │  │    │ Crawler Engine   │              │ │
│  │  │ Obfuscator  │  │    │ Network Analyzer │              │ │
│  │  │ Router      │  │    │ Report Generator │              │ │
│  │  │ Assembler   │  │    │ DB Manager       │              │ │
│  │  └─────────────┘  │    └──────────────────┘              │ │
│  │                    │                                      │ │
│  │  ┌─────────────────┴──────────────────┐                  │ │
│  │  │         MODEL POOL                  │                  │ │
│  │  │  ┌──────┐┌──────┐┌──────┐┌──────┐ │                  │ │
│  │  │  │DSeek ││Qwen  ││Claude││Ollama│ │                  │ │
│  │  │  │$0.27 ││$0.30 ││$3.00 ││$0.00 │ │                  │ │
│  │  │  │LOW   ││LOW   ││HIGH  ││MAX   │ │                  │ │
│  │  │  └──────┘└──────┘└──────┘└──────┘ │                  │ │
│  │  └────────────────────────────────────┘                  │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  ── DEPENDENCY MAP ────────────────────────────────────────── │
│  hydra_pipeline.py → hydra_obfuscator.py → hydra_router.py  │
│  hydra_router.py → moe_config.py → .env (API keys)          │
│  osint_crew.py → crewai → hydra_pipeline.py                 │
│  ─────────────────────────────────────────────────────────── │
│  📁 Files: 34 │ 🔗 Dependencies: 89 │ 📊 Complexity: Medium │
└─────────────────────────────────────────────────────────────┘
```

**Niveles de zoom:**
- **System**: Vista de pájaro — módulos principales y sus conexiones
- **Module**: Click en un módulo → ver sus componentes internos
- **Function**: Click en un componente → ver funciones, clases, métodos

**Lo que le da al Blueprint la maqueta del arquitecto:**
- React Flow en modo estático (no animado como Flow View)
- Cada nodo es clickeable → abre el código fuente en panel lateral
- Código coloreado por **clasificación Hydra**: verde (público), amarillo (propietario), rojo (clasificado)
- Las conexiones muestran dependencias reales (parseadas del código con AST analysis)
- Un botón "Generate from Code" escanea tu repo y construye el blueprint automáticamente

---

## ACCESO REMOTO DESDE EL TELÉFONO

### Arquitectura de acceso remoto

```
TELÉFONO (Android/iOS)
    │
    │  Tailscale VPN (peer-to-peer, encriptado)
    │  IP interna: 100.x.x.x
    │
    ├──→ https://100.x.x.x:3000 (PWA - mismo React UI)
    │
    │  El mismo frontend React se sirve como PWA.
    │  Progressive Web App = se instala como app nativa.
    │  Funciona offline para ver último estado cacheado.
    │  Push notifications via Service Worker.
    │
DELL OPTIPLEX (tu PC, encendida en casa)
    │
    ├── FastAPI backend (0.0.0.0:8765)
    │   ├── WebSocket: real-time updates
    │   └── REST: commands, queries
    │
    ├── Tailscale daemon (auto-connect)
    │
    └── Tauri app (UI local, también accesible via browser)
```

### ¿Por qué Tailscale?

- **Zero-config**: Instalar, login, funciona. No hay puertos que abrir, no hay DNS que configurar.
- **Peer-to-peer**: Tu teléfono se conecta directamente a tu PC. No pasa por ningún servidor intermedio.
- **Encriptado**: WireGuard bajo el capó. Estándar militar.
- **Gratis**: El plan personal es gratuito para hasta 100 dispositivos.
- **No expones nada a internet**: Tu PC no tiene ningún puerto abierto al mundo.

### Flujo de uso típico (día de delivery):

```
5:50 AM  → Abres MW-VISION en desktop
           → "Run OSINT batch-7, Hydra L4. Run MindWareHouse feature crew."
           → Sistema confirma plan y costos estimados
           → "Go."

5:55 AM  → Sales para delivery. MW-VISION minimiza a system tray.
           → Pipelines corriendo en background.

7:30 AM  → 📱 Push notification: "Batch-7 complete. 23/23. $0.11. 3 anomalies."
           → Abres PWA en el teléfono desde Tailscale
           → Ves Team View: todos los agentes idle excepto feature crew
           → Ves Flow View: feature crew al 60%
           → Todo bien. Cierras.

8:45 AM  → 📱 Push: "⚠️ Feature crew - DeepSeek timeout on fragment #7. Retrying."
           → Abres PWA → Team View → ves DeepSeek en rojo
           → Tap [Retry with Qwen] → reasignas el fragmento
           → Cierras.

2:30 PM  → Llegas a casa.
           → Abres MW-VISION en desktop
           → Chat: "Show me today's results"
           → Todo completado. Revisas outputs. Apruebas. Siguiente batch.
```

---

## CÓMO SE INTEGRA CON TU STACK ACTUAL

### Lo que YA tienes y NO cambia:

| Componente actual | Status | MW-VISION lo envuelve |
|---|---|---|
| MOE routing (moe_config.py) | ✅ Funciona | Lo visualiza en Flow View |
| Hydra Protocol (hydra_pipeline.py) | ✅ Funciona | Lo visualiza en Flow View + Blueprint |
| CrewAI crews | ✅ Funciona | Los muestra en Team View |
| Ollama local | ✅ Funciona | Lo muestra como agente en Team View |
| API keys (.env) | ✅ Funciona | Las lee el backend, nunca las expone |
| mw-route.ps1 | ✅ Funciona | El Chat lo reemplaza gradualmente |

### Lo que MW-VISION AÑADE:

| Nuevo componente | Función |
|---|---|
| `mw_vision_backend.py` | FastAPI server: WebSocket hub + REST API + task queue |
| `mw_vision_events.py` | Event emitter: cada paso del pipeline emite un evento |
| `mw_vision_db.py` | SQLite: persiste historial, métricas, configuración |
| `React frontend/` | Las 4 vistas + componentes compartidos |
| `Tauri shell/` | Empaqueta todo como .exe nativo Windows |

### Integración no-invasiva:

Tu código actual NO se modifica masivamente. MW-VISION se conecta mediante un **Event Bus**:

```python
# En tu hydra_pipeline.py actual, añades UNA línea por paso:
class HydraPipeline:
    async def execute(self, task):
        # Paso existente:
        fragments = self.decomposer.decompose(task)
        
        # NUEVA LÍNEA — emite evento:
        await self.events.emit("hydra.decomposed", {
            "task_id": task.id,
            "fragments": len(fragments),
            "trust_level": task.trust_level
        })
        
        # Paso existente:
        for fragment in fragments:
            obfuscated = self.obfuscator.obfuscate(fragment)
            
            # NUEVA LÍNEA:
            await self.events.emit("hydra.fragment.obfuscated", {
                "fragment_id": fragment.id,
                "obfuscation_level": fragment.level
            })
            
            result = await self.router.route(obfuscated)
            
            # NUEVA LÍNEA:
            await self.events.emit("hydra.fragment.completed", {
                "fragment_id": fragment.id,
                "model": result.model,
                "cost": result.cost,
                "tokens": result.tokens
            })
```

El frontend escucha estos eventos via WebSocket y actualiza los nodos en tiempo real.

---

## PLAN DE IMPLEMENTACIÓN

### FASE 1 — FOUNDATION (Semana 1-2): "Ver algo"

**Objetivo:** Tener las 4 vistas funcionando con datos simulados.

```
Día 1-2: Scaffold
  → npx create-tauri-app mw-vision --template react-ts
  → Instalar: React Flow, Zustand, shadcn/ui, Recharts, Tailwind
  → Configurar FastAPI sidecar con PyInstaller
  → Verificar que Tauri + React + FastAPI comunican via WebSocket

Día 3-5: Las 4 Vistas (con mock data)
  → Flow View: 5 nodos estáticos conectados, colores por estado
  → Team View: 4 tarjetas de agentes con status hardcodeado
  → Chat View: Input box + historial básico
  → Blueprint View: Diagrama estático del sistema

Día 6-7: WebSocket live
  → FastAPI emite eventos de prueba cada 2 segundos
  → Frontend actualiza nodos en tiempo real
  → Primer "¡está vivo!" moment
```

**Entregable Fase 1:** App Tauri que abre, muestra 4 tabs, nodos se mueven con datos fake. No conectada al MOE real.

### FASE 2 — CONNECTION (Semana 3-4): "Ver lo real"

**Objetivo:** Conectar MW-VISION al stack MOE/Hydra real.

```
Día 8-10: Event Bus
  → Implementar mw_vision_events.py
  → Añadir emit() a hydra_pipeline.py (5-10 líneas)
  → Añadir emit() a moe routing
  → Añadir emit() a CrewAI callbacks

Día 11-13: Live Flow View
  → Los nodos reales aparecen cuando lanzas una tarea
  → Colores cambian en tiempo real
  → Cost tracker actualiza cada fragmento completado

Día 14: Team View Live
  → Agentes reales: DeepSeek, Qwen, Claude, Ollama
  → Status real de cada uno
  → Tokens y costos en vivo
```

**Entregable Fase 2:** Lanzas una tarea Hydra desde Chat y VES el flujo completo en Flow View con datos reales.

### FASE 3 — MOBILE (Semana 5): "Ver desde el camión"

```
Día 15-16: Tailscale setup
  → Instalar Tailscale en PC y teléfono
  → Configurar FastAPI para servir React frontend como PWA
  → Probar acceso desde teléfono via 100.x.x.x

Día 17-18: Push notifications
  → Service Worker para PWA
  → FastAPI emite push cuando tarea completa o error
  → Botones de acción rápida en notificación

Día 19-21: Mobile-optimized views
  → Responsive layout para las 4 vistas
  → Touch-friendly: botones grandes, gestos de swipe
  → Quick actions: "Retry", "Cancel", "Approve"
```

**Entregable Fase 3:** Durante delivery, recibes push, abres PWA, ves status, reasignas tarea fallida, cierras. 30 segundos.

### FASE 4 — BLUEPRINT (Semana 6): "Ver los planos"

```
Día 22-24: AST Parser
  → Script Python que parsea tu codebase
  → Genera JSON de módulos, clases, funciones, dependencias
  → Clasifica por nivel Hydra (público, propietario, clasificado)

Día 25-27: Blueprint Generator
  → React Flow renderiza el JSON como diagrama arquitectónico
  → Zoom levels: System → Module → Function
  → Color coding por clasificación de seguridad
  → Click en nodo → panel lateral con código fuente

Día 28: Integration
  → Botón "Refresh Blueprint" re-escanea el código
  → Chat: "Show me the auth module" → navega al nodo correcto
```

**Entregable Fase 4:** Abres Blueprint View y VES la maqueta completa de tu sistema. Click en cualquier módulo → ves su anatomía interna.

---

## RECURSOS DE HARDWARE

### Dell OptiPlex 32GB (actual):

| Recurso | Tauri + MW-VISION | Ollama (14B) | Disponible |
|---|---|---|---|
| RAM | ~200MB (Tauri) + ~300MB (FastAPI) | ~10GB | ~21GB libre |
| CPU | Minimal (WebView2 nativo) | Moderate | ✅ OK |
| Disco | ~50MB (app) + ~100MB (SQLite) | Modelos existentes | ✅ OK |
| GPU | No necesita | Ya en uso | ✅ OK |

**Comparación con Electron:** Una app Electron equivalente usaría ~500MB-1GB de RAM (por empaquetar Chromium). Tauri usa ~200MB porque reutiliza WebView2 de Windows, que ya está instalado.

### Con Ryzen 9 128GB (futuro):
- Ollama con modelos 70B como assembler local
- Múltiples pipelines simultáneos
- Blueprint parsing de codebases grandes instantáneo

---

## DIFERENCIADOR: POR QUÉ ESTO ES UN PRODUCTO

Victor, MW-VISION no es solo tu herramienta. Es **el producto que MindWareHouse puede vender**.

Piénsalo: ¿Quién más tiene este problema?

- **Cualquier empresa** usando múltiples LLMs necesita visualizar el routing
- **Cualquier equipo** con agentes AI necesita ver qué están haciendo
- **Cualquier organización** preocupada por IP necesita ver qué se expone

MW-VISION es el **control room** que la industria de AI agents todavía no tiene. Las herramientas actuales (LangSmith, LangFuse, AgentOps) son dashboards de métricas. MW-VISION es un **centro de comando visual en tiempo real**.

Eso es un producto. Con tu nombre. One Step Ahead.

---

## FUENTES Y REFERENCIAS TÉCNICAS

| Tecnología | Recurso | URL |
|---|---|---|
| Tauri 2.0 | Documentación oficial | v2.tauri.app |
| Tauri + FastAPI Template | GitHub template oficial | github.com/tauri-apps/awesome-tauri (tauri-fastapi-full-stack-template) |
| Tauri v2 + Python Sidecar | Ejemplo funcional | github.com/dieharders/example-tauri-v2-python-server-sidecar |
| PyTauri | Bindings Python para Tauri | github.com/pytauri/pytauri |
| React Flow | Librería de nodos interactivos | reactflow.dev (30k+ GitHub stars) |
| React Flow AI Workflow | Template oficial para AI workflows | reactflow.dev/ui/templates/ai-workflow-editor |
| React Flow + AI Agents | Tutorial completo | damiandabrowski.medium.com (Day 90 Agentic Engineer) |
| shadcn/ui | Componentes React con Tailwind | ui.shadcn.com |
| Zustand | State management minimal | github.com/pmndrs/zustand |
| Recharts 3.0 | Charts React sobre D3 | recharts.org |
| FastAPI WebSockets | Documentación oficial | fastapi.tiangolo.com/advanced/websockets |
| Tailscale | VPN mesh peer-to-peer | tailscale.com |
| Tauri WebSocket Plugin | Plugin oficial | v2.tauri.app/plugin/websocket |
| CodexMonitor | Ejemplo de Tauri para agent orchestration | sourceforge.net/projects/codexmonitor.mirror |

---

## RESUMEN EJECUTIVO

**Problema:** Tienes un motor V8 pero estás conduciendo a ciegas.

**Solución:** MW-VISION — una app de escritorio Windows nativa (Tauri 2.0) con 4 vistas:
1. **Flow View** — Cómo fluye la información (React Flow, nodos vivos)
2. **Team View** — Quién trabaja en qué (tarjetas de agentes en tiempo real)
3. **Chat View** — Tu puente de mando (comandos naturales)
4. **Blueprint View** — Los planos del edificio (arquitectura completa)

**Acceso remoto:** Tailscale VPN + PWA → control total desde el teléfono durante delivery.

**Stack:** Tauri 2.0 (Rust shell) + React/TypeScript (UI) + FastAPI (Python backend) + WebSockets (real-time) + SQLite (persistencia).

**Tiempo:** 6 semanas. Fase 1 (ver algo) en 7 días.

**Costo:** $0. Todo open source. Corre en tu Dell actual.

**Impacto:** De "vibe coding a ciegas" a "dirigir una orquesta con partitura completa."

**Futuro:** MW-VISION no es solo tu herramienta. Es el producto que le falta a la industria de AI agents.
