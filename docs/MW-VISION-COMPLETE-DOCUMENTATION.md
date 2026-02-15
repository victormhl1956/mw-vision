# MW-VISION: Complete Feature Documentation
## Visual Command Center for AI Agent Orchestration

**Document Version:** 2.0  
**Date:** February 14, 2026  
**Company:** MindWareHouse  
**Author:** Development Team

---

## Executive Introduction

MW-VISION representa la evolución definitiva en la orquestación de agentes AI. Este documento consolida toda la documentación técnica, especificaciones de features, y detalles de implementación en una única referencia autoritativa para el proyecto.

### What is MW-VISION?

MW-VISION es un **Centro de Comando Visual** diseñado específicamente para resolver el problema fundamental de visibilidad en el desarrollo asistido por múltiples modelos AI. Mientras las herramientas actuales (LangSmith, AgentOps) ofrecen dashboards retrospectivos, MW-VISION proporciona **control en tiempo real** con intervención dinámica.

### Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| **Real-Time Visualization** | Nodos vivos que muestran el flujo de datos entre agentes mientras ejecutan |
| **Cost Circuit Breakers** | Límites de presupuesto que pausan automáticamente antes de exceder |
| **Hydra Protocol Integration** | Protección de IP mediante fragmentación de código para modelos no confiables |
| **Mobile Command Center** | Control total desde cualquier dispositivo via Tailscale VPN + PWA |
| **Framework Agnostic** | Compatible con CrewAI, AutoGen, LangGraph, y cualquier framework personalizado |

### Current Development Status

| Phase | Status | Completion |
|-------|--------|------------|
| **Frontend (React + TypeScript)** | ✅ Complete | 100% |
| **Backend (FastAPI)** | ✅ Complete | 100% |
| **WebSocket Real-Time** | ✅ Complete | 100% |
| **Chrome DevTools MCP** | ✅ Complete | 100% |
| **Zustand State Management** | ✅ Complete | 100% |
| **Toast Notification System** | ✅ Complete | 100% |
| **Cost Tracking** | ✅ Complete | 100% |
| **Agent Detail Modals** | ✅ Complete | 100% |
| **Real Connection Status** | ✅ Complete | 100% |
| **Error Boundaries** | ⏳ Pending | 0% |
| **Test Coverage** | ⏳ Pending | 0% |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Frontend Components](#2-frontend-components)
3. [Backend Services](#3-backend-services)
4. [State Management](#4-state-management)
5. [WebSocket Communication](#5-websocket-communication)
6. [Views Documentation](#6-views-documentation)
7. [Features Detail](#7-features-detail)
8. [UI Design System](#8-ui-design-system)
9. [Security & Hydra Protocol](#9-security--hydra-protocol)
10. [Development Guide](#10-development-guide)
11. [Deployment](#11-deployment)

---

## 1. Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MW-VISION PLATFORM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              TAURI DESKTOP SHELL (Rust)                    │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │           REACT FRONTEND (WebView2)                 │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │   │   │
│  │  │  │ FLOW    │ │ TEAM    │ │ CHAT    │ │BLUEPRINT│  │   │   │
│  │  │  │ VIEW    │ │ VIEW    │ │ VIEW    │ │ VIEW    │  │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘  │   │   │
│  │  │                                                      │   │   │
│  │  │              ZUSTAND STORE                            │   │   │
│  │  │              (Global State)                           │   │   │
│  │  │                                                      │   │   │
│  │  │        WEBSOCKET SERVICE (Real-Time Updates)          │   │   │
│  │  │                                                      │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                    │
│                    WebSocket (ws://localhost:8000/ws)              │
│                              │                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              FASTAPI BACKEND (Python)                       │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │   │
│  │  │WebSocket     │  │ REST API     │  │ Agent Engine   │  │   │
│  │  │Manager       │  │ Endpoints    │  │ (Simulation)   │  │   │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │   │
│  │  │ Cost Tracker │  │ Crew Control │  │ Event Bus      │  │   │
│  │  └──────────────┘  └──────────────┘  └────────────────┘  │   │
│  │                                                             │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend Framework** | React | 18.3.1 | UI Components |
| **Language** | TypeScript | 5.x | Type Safety |
| **Build Tool** | Vite | Latest | Fast Development |
| **State Management** | Zustand | 4.5.2 | Global State |
| **Visual Workflow** | @xyflow/react | 12.3.5 | Node-based Canvas |
| **Styling** | Tailwind CSS | Latest | Utility Classes |
| **Icons** | Lucide React | Latest | Icon System |
| **Backend** | FastAPI | Latest | REST + WebSocket |
| **Web Server** | Uvicorn | Latest | ASGI Server |
| **Desktop Shell** | Tauri | 2.0 | Native Windows App |

---

## 2. Frontend Components

### Component Hierarchy

```
src/
├── main.tsx                    # Entry point + ToastProvider
├── App.tsx                     # Main app shell + tabs
├── index.css                   # Global styles + glassmorphism
├── components/
│   ├── Toast.tsx              # Notification system
│   └── FlowCanvas.tsx         # React Flow integration
├── views/
│   ├── FlowView.tsx           # Visual workflow canvas
│   ├── TeamView.tsx           # Agent dashboard
│   ├── ChatView.tsx           # Command interface
│   └── BlueprintView.tsx      # Code import + Hydra
├── stores/
│   └── crewStore.ts           # Zustand state management
└── services/
    └── websocketService.ts    # WebSocket communication
```

### Core Components

#### 2.1 Toast Notification System

**File:** `src/components/Toast.tsx`

El sistema Toast proporciona feedback en tiempo real con语义 colors.

```typescript
interface Toast {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
}

function showToast(type, title, message)
function showSuccess(title, message)
function showError(title, message)
function showWarning(title, message)
function showInfo(title, message)
```

**Usage:**
```typescript
import { useToast } from '../components/Toast'

// Show success notification
toast.showSuccess('Crew Launched', 'Agents are now running')

// Show error notification  
toast.showError('Connection Failed', 'Backend is not responding')
```

**Features:**
- Auto-dismiss configurable por duración
- Dismiss manual con botón X
- Semantic colors (verde éxito, rojo error, naranja warning, cyan info)
- Animaciones suaves de entrada/salida
- Stacking de múltiples toasts

---

## 3. Backend Services

### 3.1 FastAPI Application

**File:** `backend/main.py`

El backend proporciona endpoints REST y WebSocket para comunicación en tiempo real.

#### WebSocket Endpoint

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agent updates."""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            "type": "init",
            "data": {
                "agents": [a.model_dump() for a in agents.values()],
                "crew": crew_state.model_dump()
            }
        })
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_message(message)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

#### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check with crew status |
| `/api/agents` | GET | List all agents |
| `/api/crew` | GET | Get crew state |

#### Crew Commands

```typescript
// Launch all agents
await ws.send({
  type: 'crew_command',
  data: { command: 'launch' }
})

// Pause all agents
await ws.send({
  type: 'crew_command', 
  data: { command: 'pause' }
})

// Stop all agents
await ws.send({
  type: 'crew_command',
  data: { command: 'stop' }
})

// Control individual agent
await ws.send({
  type: 'agent_command',
  agentId: '1',
  data: { command: 'pause' }
})
```

### 3.2 Agent Simulation

El backend simula actividad de agentes con costos realistas:

```python
MODEL_COSTS = {
    "claude-3-5-sonnet": 0.015,  # $0.015 per 1K tokens
    "deepseek-chat": 0.002,       # $0.002 per 1K tokens  
    "gpt-4o": 0.03,              # $0.03 per 1K tokens
    "gpt-4": 0.06,               # $0.06 per 1K tokens
    "ollama": 0,                  # Free (local)
}

async def simulate_agent_updates():
    """Background task to simulate agent activity."""
    while True:
        if crew_state.is_running:
            for agent_id, agent in agents.items():
                if agent.status == AgentStatus.RUNNING:
                    # Simulate token usage (100-600 tokens)
                    tokens = random.randint(100, 600)
                    cost_per_token = MODEL_COSTS.get(agent.model, 0.01)
                    cost_increment = (tokens / 1000) * cost_per_token
                    
                    # Update agent cost
                    agent.cost = round(agent.cost + cost_increment, 4)
                    
                    # Check budget
                    if crew_state.total_cost > crew_state.budget_limit:
                        crew_state.is_running = False
                        await manager.broadcast({
                            "type": "crew_status",
                            "data": {
                                "is_running": False,
                                "message": "Budget limit exceeded"
                            }
                        })
        await asyncio.sleep(2)
```

---

## 4. State Management

### 4.1 Zustand Crew Store

**File:** `src/stores/crewStore.ts`

El store centraliza todo el estado de la aplicación.

#### Agent Interface

```typescript
export interface Agent {
  id: string
  name: string
  model: string
  status: 'idle' | 'running' | 'paused' | 'error'
  cost: number
  lastUpdate: number
  tasks: number
  averageResponseTime: number
}
```

#### Store Interface

```typescript
interface CrewState {
  // Data
  agents: Agent[]
  isCrewRunning: boolean
  totalCost: number
  estimatedCost: number
  budgetLimit: number
  connectionStatus: ConnectionStatus
  
  // Actions - Core Crew Management
  launchCrew: () => void
  pauseCrew: () => void
  resetCrew: () => void
  
  // Actions - Agent Management
  addAgent: (agent: Agent) => void
  removeAgent: (id: string) => void
  updateAgentStatus: (id: string, status: Agent['status']) => void
  updateAgentCost: (id: string, cost: number) => void
  
  // Actions - Cost & Budget
  setEstimatedCost: (cost: number) => void
  setBudgetLimit: (limit: number) => void
  checkBudgetLimit: () => boolean
  
  // Actions - Connection Management
  setConnectionStatus: (status: ConnectionStatus) => void
  setCrewRunning: (running: boolean) => void
}
```

#### Connection Status

```typescript
export type ConnectionStatus = 
  | 'disconnected'    // No connection
  | 'connecting'       // Attempting connection
  | 'connected'        // Real WebSocket connection
  | 'error'           // Connection error
  | 'simulating'      // Fallback simulation mode
```

#### Key Features

**Circuit Breaker:**
```typescript
updateAgentCost: (id: string, cost: number) => {
  set((state) => {
    const updatedAgents = state.agents.map((agent) =>
      agent.id === id ? { ...agent, cost } : agent
    )
    const newTotalCost = updatedAgents.reduce((sum, a) => sum + a.cost, 0)
    
    // Auto-pause if budget exceeded
    if (newTotalCost > state.budgetLimit && state.isCrewRunning) {
      console.warn('Circuit breaker triggered')
      const pausedAgents = updatedAgents.map((a) => 
        a.status === 'running' ? { ...a, status: 'paused' } : a
      )
      return { 
        agents: pausedAgents, 
        totalCost: newTotalCost,
        isCrewRunning: false
      }
    }
    
    return { agents: updatedAgents, totalCost: newTotalCost }
  })
}
```

---

## 5. WebSocket Communication

### 5.1 WebSocket Service

**File:** `src/services/websocketService.ts`

El servicio WebSocket maneja conexión, reconexión automática, y fallback a simulación.

```typescript
class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private simulationInterval: ReturnType<typeof setInterval> | null = null
  
  connect(url: string = 'ws://localhost:8000/ws') {
    try {
      this.ws = new WebSocket(url)
      
      this.ws.onopen = () => {
        this.connectionStatus = 'connected'
        this.stopSimulation()
      }
      
      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        this.handleMessage(message)
      }
      
      this.ws.onclose = () => {
        this.scheduleReconnect()
      }
      
      this.ws.onerror = (error) => {
        this.startSimulation() // Fallback
      }
    } catch {
      this.startSimulation() // Fallback
    }
  }
  
  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.startSimulation()
      return
    }
    
    this.reconnectAttempts++
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    setTimeout(() => this.connect(this.url), delay)
  }
  
  startSimulation() {
    // Fallback simulation when backend unavailable
    this.isSimulating = true
    this.simulationInterval = setInterval(() => {
      // Simulate cost updates
    }, 2000)
  }
}
```

#### Message Types

```typescript
type WebSocketMessage =
  | { type: 'init'; data: { agents: Agent[]; crew: CrewState } }
  | { type: 'agent_update'; agentId: string; data: { status: string } }
  | { type: 'cost_update'; agentId: string; data: { cost: number } }
  | { type: 'task_complete'; agentId: string }
  | { type: 'crew_status'; data: { isRunning: boolean } }
  | { type: 'error'; data: { message: string } }
```

---

## 6. Views Documentation

### 6.1 Flow View

**File:** `src/views/FlowView.tsx`

Flow View proporciona visualización interactiva del workflow de agentes usando React Flow.

```typescript
export default function FlowView() {
  const { agents, estimatedCost, budgetLimit, isCrewRunning } = useCrewStore()
  
  return (
    <div className="space-y-4">
      {/* Cost Preview Bar */}
      <div className="glass-panel p-4">
        <div className="flex justify-between items-center">
          <span>Estimated Cost:</span>
          <span className={estimatedCost > budgetLimit ? 'text-red-500' : 'text-osint-cyan'}>
            ${estimatedCost.toFixed(2)}
          </span>
        </div>
        <Progress value={(estimatedCost / budgetLimit) * 100} />
      </div>
      
      {/* Flow Canvas */}
      <FlowCanvas agents={agents} />
      
      {/* Control Buttons */}
      <div className="flex gap-4">
        <button onClick={() => launchCrew()}>Launch Crew</button>
        <button onClick={() => pauseCrew()}>Pause All</button>
      </div>
    </div>
  )
}
```

**Features:**
- Nodos de agentes personalizados con estado visual
- Conexiones animadas mostrando flujo de datos
- MiniMap para navegación
- Zoom y pan interactivo
- Preview de costo con warning de presupuesto

---

### 6.2 Team View

**File:** `src/views/TeamView.tsx`

Team View muestra dashboard con KPIs y monitoreo de agentes.

```typescript
export default function TeamView() {
  const { agents, totalCost, isCrewRunning, connectionStatus, updateAgentStatus } = useCrewStore()
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  
  const activeAgents = agents.filter(a => a.status === 'running').length
  const totalTasks = agents.reduce((sum, a) => sum + a.tasks, 0)
  const avgResponse = agents.reduce((sum, a) => sum + a.averageResponseTime, 0) / agents.length || 0
  
  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        <KPICard title="Active Agents" value={activeAgents} icon={Zap} color="cyan" />
        <KPICard title="Total Tasks" value={totalTasks} icon={Target} color="green" />
        <KPICard title="Total Cost" value={`$${totalCost.toFixed(2)}`} icon={DollarSign} color="purple" />
        <KPICard title="Avg Response" value={`${avgResponse.toFixed(1)}s`} icon={Clock} color="orange" />
      </div>
      
      {/* Agent Cards */}
      <div className="grid grid-cols-2 gap-6">
        {agents.map(agent => (
          <AgentCard 
            agent={agent}
            onViewDetails={() => setSelectedAgent(agent)}
            onPause={() => updateAgentStatus(agent.id, 'paused')}
          />
        ))}
      </div>
      
      {/* System Status - REAL connection status */}
      <SystemStatus connectionStatus={connectionStatus} />
      
      {/* Agent Detail Modal */}
      {selectedAgent && (
        <AgentDetailModal agent={selectedAgent} onClose={() => setSelectedAgent(null)} />
      )}
    </div>
  )
}
```

**Features:**
- KPIs en tiempo real
- Tarjetas de agentes con estado, costo, y métricas
- Modal de detalles con información completa
- Sistema de estatus REAL (no hardcodeado)
- Botones funcionales de Pause/Details

---

### 6.3 Chat View

**File:** `src/views/ChatView.tsx`

Chat View proporciona interfaz de comandos en lenguaje natural.

```typescript
export default function ChatView() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const { isCrewRunning, totalCost, budgetLimit } = useCrewStore()
  
  const processCommand = (cmd: string): boolean => {
    const normalized = cmd.toLowerCase().trim()
    
    if (normalized.match(/^(launch|start|run)\s+(.*)/)) {
      useCrewStore.getState().launchCrew()
      return true
    }
    
    if (normalized.includes('pause') || normalized.includes('stop')) {
      useCrewStore.getState().pauseCrew()
      return true
    }
    
    if (normalized.includes('status')) {
      // Show status
      return true
    }
    
    if (normalized.includes('cost') || normalized.includes('budget')) {
      // Show cost info
      return true
    }
    
    if (normalized.includes('reset')) {
      useCrewStore.getState().resetCrew()
      return true
    }
    
    return false
  }
  
  return (
    <div className="space-y-6">
      {/* Messages */}
      <div className="glass-panel h-[500px] overflow-y-auto">
        {messages.map(msg => (
          <MessageBubble message={msg} />
        ))}
      </div>
      
      {/* Input */}
      <div className="flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
          placeholder="Type a command..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
      
      {/* Quick Commands */}
      <div className="grid grid-cols-4 gap-3">
        <button onClick={() => handleQuickCommand('Launch crew')}>Launch Crew</button>
        <button onClick={() => handleQuickCommand('Pause crew')}>Pause Crew</button>
        <button onClick={() => handleQuickCommand('Status')}>Status</button>
        <button onClick={() => handleQuickCommand('Cost')}>Cost Check</button>
      </div>
    </div>
  )
}
```

**Commands Supported:**
- `Launch crew` / `Start crew` / `Run crew` - Inicia todos los agentes
- `Pause crew` / `Stop crew` - Pausa todos los agentes
- `Status` - Muestra estado del crew
- `Cost` / `Budget` / `Spend` - Muestra costo actual
- `Reset` - Reinicia todos los agentes
- `Help` - Muestra comandos disponibles

---

### 6.4 Blueprint View

**File:** `src/views/BlueprintView.tsx`

Blueprint View permite importar código y aplicar protección Hydra.

```typescript
export default function BlueprintView() {
  const [importUrl, setImportUrl] = useState('')
  const [files, setFiles] = useState<FileClassification[]>([])
  const [hydraEnabled, setHydraEnabled] = useState(false)
  
  const handleImport = async () => {
    // Simulate GitHub import
    setFiles([
      { name: 'auth.py', type: 'proprietary', protected: false },
      { name: 'utils.py', type: 'public', protected: false },
      { name: 'config.py', type: 'proprietary', protected: hydraEnabled },
    ])
  }
  
  return (
    <div className="space-y-6">
      {/* Import Section */}
      <div className="glass-panel p-6">
        <h2 className="text-xl font-orbitron mb-4">GitHub Import</h2>
        <input
          value={importUrl}
          onChange={(e) => setImportUrl(e.target.value)}
          placeholder="https://github.com/username/repo"
        />
        <button onClick={handleImport}>Import Repository</button>
      </div>
      
      {/* Files Classification */}
      {files.length > 0 && (
        <div className="glass-panel p-6">
          <h2 className="text-xl font-orbitron mb-4">File Classification</h2>
          <table>
            <thead>
              <tr>
                <th>File</th>
                <th>Type</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {files.map(file => (
                <tr>
                  <td>{file.name}</td>
                  <td>{file.type}</td>
                  <td>{file.protected ? '🛡️ Protected' : '🔓 Unprotected'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {/* Hydra Controls */}
      <div className="glass-panel p-6">
        <h2 className="text-xl font-orbitron mb-4">Hydra Protocol</h2>
        <Toggle checked={hydraEnabled} onChange={setHydraEnabled} />
        <p>Enable to protect proprietary files before sending to external models</p>
      </div>
    </div>
  )
}
```

---

## 7. Features Detail

### 7.1 Cost Tracking System

#### Model Pricing

```typescript
const MODEL_COSTS = {
  'claude-3-5-sonnet': 0.015,  // $0.015 per 1K tokens
  'deepseek-chat': 0.002,       // $0.002 per 1K tokens  
  'gpt-4o': 0.03,              // $0.03 per 1K tokens
  'gpt-4': 0.06,               // $0.06 per 1K tokens
  'ollama': 0,                  // Free (local)
}
```

#### Budget Circuit Breaker

```typescript
// Default budget: $10.00
budgetLimit: number = 10.0

// Check before launching
checkBudgetLimit: () => {
  const { estimatedCost, budgetLimit } = get()
  if (estimatedCost > budgetLimit) {
    toast.showWarning('Budget Exceeded', 'Cannot launch crew')
    return true // Would exceed
  }
  return false // Safe to proceed
}

// Auto-pause on cost update
updateAgentCost: (id, cost) => {
  const newTotal = get().agents.reduce((sum, a) => sum + a.cost, 0)
  if (newTotal > get().budgetLimit) {
    get().pauseCrew()
    toast.showError('Budget Exceeded', 'Crew paused automatically')
  }
}
```

### 7.2 Real Connection Status

```typescript
const getConnectionStatus = () => {
  switch (wsService.getConnectionStatus()) {
    case 'connected':
      return { color: 'bg-green-500', label: 'Connected' }
    case 'connecting':
      return { color: 'bg-orange-500 animate-pulse', label: 'Connecting...' }
    case 'simulating':
      return { color: 'bg-purple-500', label: 'Simulation Mode' }
    case 'error':
      return { color: 'bg-red-500', label: 'Connection Error' }
    default:
      return { color: 'bg-gray-500', label: 'Disconnected' }
  }
}
```

### 7.3 Agent Detail Modal

```typescript
function AgentDetailModal({ agent, onClose }: { agent: Agent; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="glass-panel max-w-lg w-full rounded-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="text-xl font-bold text-osint-cyan">{agent.name}</h3>
            <div className="text-sm text-osint-text-dim font-mono">{agent.model}</div>
          </div>
          <button onClick={onClose}><X /></button>
        </div>
        
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <StatCard label="Status" value={agent.status} color={statusColor} />
            <StatCard label="Total Cost" value={`$${agent.cost.toFixed(4)}`} color="cyan" />
          </div>
          
          <StatCard label="Tasks Completed" value={agent.tasks} />
          <StatCard label="Avg Response Time" value={`${agent.averageResponseTime.toFixed(1)}s`} />
          <StatCard label="Last Activity" value={new Date(agent.lastUpdate).toLocaleString()} />
        </div>
      </div>
    </div>
  )
}
```

---

## 8. UI Design System

### 8.1 MindWareHouse Color Palette

```css
/* Tailwind Config */
colors: {
  osint: {
    cyan: '#00d4ff',
    purple: '#9d4edd',
    green: '#00ff88',
    orange: '#ff9900',
    red: '#ff3366',
    panel: 'rgba(10, 14, 39, 0.8)',
    text: '#e2e8f0',
    'text-dim': '#94a3b8',
    'text-muted': '#64748b',
  }
}
```

### 8.2 Glassmorphism

```css
.glass-panel {
  @apply bg-osint-panel backdrop-blur-xl border border-white/10 rounded-xl;
}

.glass-card {
  @apply bg-white/5 border border-white/10 rounded-lg;
}
```

### 8.3 Typography

```css
/* Headers */
font-family: 'Orbitron', sans-serif;

/* Code */
font-family: 'JetBrains Mono', monospace;

/* Body */
font-family: 'Inter', sans-serif;
```

---

## 9. Security & Hydra Protocol

### 9.1 Hydra Protocol Overview

El Hydra Protocol es un sistema de protección de IP que fragmenta código antes de enviarlo a modelos externos no confiables.

**Protection Levels:**

| Level | Protection | Use Case |
|-------|------------|----------|
| **L0** | None | Public code, no IP concerns |
| **L1** | Variable renaming | Minor proprietary logic |
| **L2** | Fragmentation + renaming | Core business logic |
| **L3** | Fragmentation + schema rotation | Sensitive algorithms |
| **L4** | Full obfuscation + steganography | Maximum protection |

### 9.2 Fragmentation Process

```python
class HydraProtocol:
    def fragment(self, code: str, level: int) -> List[Fragment]:
        """Split code into protected fragments."""
        fragments = []
        
        if level >= 2:
            # Split into logical chunks
            chunks = self.parse_into_chunks(code)
            for chunk in chunks:
                fragments.append(Fragment(
                    content=self.obfuscate(chunk, level),
                    markers=self.add_markers(chunk),
                    schema_rotation=level >= 3
                ))
        
        return fragments
    
    def obfuscate(self, code: str, level: int) -> str:
        """Apply obfuscation based on protection level."""
        code = self.rename_variables(code)  # L1+
        code = self.remove_comments(code)    # L2+
        code = self.add_noise(code)          # L3+
        code = self.hide_patterns(code)      # L4
        return code
```

---

## 10. Development Guide

### 10.1 Setup

```bash
# Clone repository
cd MW-Vision

# Install dependencies
cd mw-vision-app
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### 10.2 Running Development Server

```bash
# Terminal 1: Frontend
cd mw-vision-app
npm run dev

# Terminal 2: Backend
cd backend
python main.py
```

**Access:** http://localhost:5189

### 10.3 Building for Production

```bash
# Frontend build
cd mw-vision-app
npm run build

# Backend build (PyInstaller)
cd backend
pyinstaller --onefile main.py
```

---

## 11. Deployment

### 11.1 Desktop (Tauri)

```bash
# Install Tauri CLI
cargo install tauri-cli

# Build for Windows
npm run tauri build --target windows
```

### 11.2 Backend

```bash
# Using Gunicorn
gunicorn -k uvicorn.workers.UvicornWorker main:app

# Using Docker
docker build -t mw-vision-backend .
docker run -p 8000:8000 mw-vision-backend
```

### 11.3 Environment Variables

```bash
# Backend (.env)
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8000
DEFAULT_BUDGET=10.0

# Frontend (.env)
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Appendix A: File Reference

| File | Purpose |
|------|---------|
| `src/main.tsx` | Entry point, ToastProvider wrapper |
| `src/App.tsx` | Main app shell, tab navigation |
| `src/components/Toast.tsx` | Notification system |
| `src/components/FlowCanvas.tsx` | React Flow canvas |
| `src/views/FlowView.tsx` | Flow visualization view |
| `src/views/TeamView.tsx` | Agent dashboard view |
| `src/views/ChatView.tsx` | Command interface view |
| `src/views/BlueprintView.tsx` | Code import + Hydra view |
| `src/stores/crewStore.ts` | Zustand state management |
| `src/services/websocketService.ts` | WebSocket client |
| `backend/main.py` | FastAPI backend |
| `docs/MW-VISION-Architecture.md` | Architecture documentation |
| `docs/MW-VISION-EXECUTIVE-SUMMARY.md` | Market analysis |
| `docs/MW-VISION-TECHNICAL-SPECIFICATION.md` | Technical specs |

---

## Appendix B: Changelog

### Version 2.0 (February 14, 2026)

**New Features:**
- ✅ Real WebSocket connection with backend
- ✅ Agent Detail Modal with full statistics
- ✅ Real connection status (no more hardcoded "Connected")
- ✅ Functional Pause/Details buttons on agent cards
- ✅ Custom SVG favicon with MW-Vision branding
- ✅ SEO meta tags and Open Graph support
- ✅ Budget circuit breaker implementation
- ✅ Chrome DevTools MCP integration

**Bug Fixes:**
- Fixed FlowCanvas useMemo anti-pattern (changed to useEffect)
- Fixed ChatView onKeyPress deprecated (now onKeyDown)
- Fixed WebSocket never connecting (implemented real connection)
- Fixed Chat only doing console.log (now processes commands)

**Documentation:**
- Created this comprehensive documentation
- Updated README.md with current features

---

## Appendix C: Credits

**Development Team:** MindWareHouse  
**Lead Developer:** Victor Hernandez  
**Documentation:** Claude AI Assistant

---

*Document Version: 2.0*  
*Last Updated: February 14, 2026*  
*One Step Ahead*
