# MW-VISION: Complete Technical Specification
## Developer Implementation Guide for AI-Code Agents

**Document Version:** 1.0  
**Date:** February 2026  
**Target Audience:** AI Code Agents, Software Developers  
**Estimated Implementation Time:** 6 weeks (1 developer)  

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Phase 1: Foundation Setup](#phase-1-foundation-setup)
6. [Phase 2: Core Backend](#phase-2-core-backend)
7. [Phase 3: Frontend Implementation](#phase-3-frontend-implementation)
8. [Phase 4: Integration & Testing](#phase-4-integration--testing)
9. [Phase 5: Mobile & Security](#phase-5-mobile--security)
10. [Phase 6: Deployment](#phase-6-deployment)
11. [Appendices](#appendices)

---

## System Overview

### What We're Building

MW-Vision is a **Tauri 2.0 desktop application** that provides visual command and control for multi-agent AI workflows. Think of it as "Mission Control for AI Development."

**Core Features:**
- **Flow View**: Real-time visual node graph of agent execution (React Flow)
- **Team View**: Agent status dashboard with live metrics
- **Chat View**: Natural language command interface
- **Blueprint View**: System architecture visualization
- **Mobile Access**: Progressive Web App via Tailscale VPN
- **Hydra Protocol**: Built-in code obfuscation for IP protection

### Technology Decision Matrix

| Technology | Purpose | Why This Choice |
|------------|---------|-----------------|
| **Tauri 2.0** | Desktop shell | 50% less RAM than Electron, native WebView2, Rust security |
| **React + TypeScript** | Frontend UI | Largest ecosystem, React Flow for nodes, shadcn/ui components |
| **React Flow** | Visual graphs | Industry standard for node-based UIs (Stripe, Typeform use it) |
| **FastAPI** | Backend API | Python ecosystem (CrewAI, Langfuse), async support, WebSockets |
| **SQLite** | Local database | Zero-config, single file, perfect for desktop apps |
| **WebSockets** | Real-time comms | Bi-directional, low latency, native Tauri + FastAPI support |
| **Zustand** | State management | Minimal boilerplate, recommended by React Flow |
| **Tailscale** | Remote access | Zero-config P2P VPN, works through NAT |

---

## Architecture

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  TAURI 2.0 DESKTOP APPLICATION (Rust + WebView2)            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  REACT FRONTEND (TypeScript)                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────┐ ┌────────────┐  │  │
│  │  │ Flow     │ │ Team     │ │ Chat │ │ Blueprint  │  │  │
│  │  │ View     │ │ View     │ │ View │ │ View       │  │  │
│  │  │          │ │          │ │      │ │            │  │  │
│  │  │ React    │ │ Agent    │ │ NL   │ │ Arch       │  │  │
│  │  │ Flow     │ │ Cards    │ │ Input│ │ Diagram    │  │  │
│  │  └─────┬────┘ └─────┬────┘ └───┬──┘ └──────┬─────┘  │  │
│  │        │             │          │           │         │  │
│  │        └─────────────┴──────────┴───────────┘         │  │
│  │                      │                                 │  │
│  │              ┌───────▼───────┐                         │  │
│  │              │   Zustand     │                         │  │
│  │              │   Store       │                         │  │
│  │              └───────┬───────┘                         │  │
│  │                      │ WebSocket (ws://localhost:8765) │  │
│  └──────────────────────┼─────────────────────────────────┘  │
│                         │                                     │
│  ┌──────────────────────▼─────────────────────────────────┐  │
│  │  FASTAPI BACKEND (Python Sidecar)                      │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ │  │
│  │  │ WebSocket    │ │ Event Bus    │ │ Task Queue     │ │  │
│  │  │ Manager      │ │              │ │                │ │  │
│  │  └──────────────┘ └──────────────┘ └────────────────┘ │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ │  │
│  │  │ Hydra        │ │ CrewAI       │ │ Langfuse       │ │  │
│  │  │ Protocol     │ │ Integration  │ │ Client         │ │  │
│  │  └──────────────┘ └──────────────┘ └────────────────┘ │  │
│  │         ↕ SQLite (mw-vision.db)                        │  │
│  └────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
              ↕
┌─────────────────────────────────────────────────────────────┐
│  EXTERNAL SERVICES                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ OpenRouter│ │ Anthropic│ │ Langfuse │ │ AgentOps      │  │
│  │ API       │ │ API      │ │ Server   │ │ (optional)    │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow: Example "Run Bug Hunting Crew"

```
1. USER COMMAND
   Chat View → "Run bug hunting crew on network_analysis.py"
   
2. FRONTEND PROCESSING
   ChatInput.tsx → parsers natural language
   → Determines: crew=bug_hunter, file=network_analysis.py
   → Sends WebSocket message: { action: "launch_crew", crew: "bug_hunter", context: {...} }
   
3. BACKEND RECEIVES
   WebSocketManager.on_message() → routes to CrewAIService
   → CrewAIService.launch_crew("bug_hunter", context)
   → Stores task in SQLite with status="initializing"
   
4. CREWAI EXECUTION BEGINS
   → CrewAI creates 4 agents (Architect, Debugger, Security, Implementer)
   → Each agent execution emits events:
      - "agent.started" → { agent_id, agent_role, model }
      - "agent.thinking" → { agent_id, thought_process }
      - "agent.completed" → { agent_id, output, tokens, cost }
   
5. EVENTS BROADCAST VIA WEBSOCKET
   EventBus.emit("agent.started") 
   → WebSocketManager.broadcast_to_all(event)
   → Frontend receives event
   
6. FRONTEND UPDATES
   Zustand store receives event → updates state
   → FlowView re-renders → new node appears with "Architect" label, status="active"
   → TeamView re-renders → Architect card shows "thinking", elapsed time updates
   → Cost tracker increments
   
7. REAL-TIME UPDATES (every agent action)
   Agent completes → event → frontend updates → user sees progress
   
8. COMPLETION
   Final agent (Implementer) completes
   → EventBus.emit("crew.completed", { result, total_cost, total_time })
   → ChatView displays result
   → FlowView shows all nodes green
   → SQLite task updated to status="completed"
```

---

## Technology Stack

### Core Dependencies (Exact Versions)

```json
// package.json (Frontend)
{
  "name": "mw-vision",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "tauri": "tauri"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@xyflow/react": "^12.3.5",
    "zustand": "^4.5.2",
    "recharts": "^3.0.0",
    "lucide-react": "^0.460.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.0",
    "@tauri-apps/api": "^2.1.1",
    "@tauri-apps/plugin-websocket": "^2.0.0",
    "date-fns": "^4.1.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.3",
    "typescript": "^5.6.3",
    "vite": "^6.0.1",
    "@tauri-apps/cli": "^2.1.0",
    "tailwindcss": "^3.4.15",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49"
  }
}
```

```toml
# Cargo.toml (Tauri Backend - Rust)
[package]
name = "mw-vision"
version = "0.1.0"
edition = "2021"

[build-dependencies]
tauri-build = { version = "2.0", features = [] }

[dependencies]
tauri = { version = "2.1", features = ["tray-icon", "image-ico", "image-png"] }
tauri-plugin-websocket = "2.0"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["full"] }
```

```python
# requirements.txt (Python Backend)
fastapi==0.115.5
uvicorn[standard]==0.32.1
websockets==14.1
sqlalchemy==2.0.36
sqlmodel==0.0.22
pydantic==2.10.3
python-dotenv==1.0.1

# CrewAI Integration
crewai[tools]==0.86.0
langchain==0.3.12

# Observability
langfuse==2.56.1
agentops==0.3.17

# Utilities
python-multipart==0.0.20
aiofiles==24.1.0
rich==13.9.4
```

---

## Project Structure

### Complete Directory Tree

```
mw-vision/
├── src-tauri/                    # Tauri Rust backend
│   ├── src/
│   │   ├── main.rs              # Tauri entry point
│   │   ├── commands.rs          # Tauri commands exposed to frontend
│   │   └── lib.rs               # Library exports
│   ├── Cargo.toml               # Rust dependencies
│   ├── tauri.conf.json          # Tauri configuration
│   ├── icons/                   # App icons (ico, png)
│   └── build.rs                 # Build script
│
├── src/                          # React frontend
│   ├── main.tsx                 # React entry point
│   ├── App.tsx                  # Root component with routing
│   ├── index.css                # Global styles (Tailwind)
│   │
│   ├── components/              # React components
│   │   ├── ui/                  # shadcn/ui primitives
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── ...
│   │   │
│   │   ├── flow/                # Flow View components
│   │   │   ├── FlowCanvas.tsx   # Main React Flow canvas
│   │   │   ├── CustomNode.tsx   # Custom node component
│   │   │   ├── EdgeLabel.tsx    # Animated edge labels
│   │   │   └── MiniMap.tsx      # Minimap overlay
│   │   │
│   │   ├── team/                # Team View components
│   │   │   ├── AgentCard.tsx    # Individual agent card
│   │   │   ├── AgentGrid.tsx    # Grid layout
│   │   │   └── CostChart.tsx    # Cost breakdown chart
│   │   │
│   │   ├── chat/                # Chat View components
│   │   │   ├── ChatInput.tsx    # Command input
│   │   │   ├── Message.tsx      # Message bubble
│   │   │   └── CommandSuggestions.tsx
│   │   │
│   │   └── blueprint/           # Blueprint View components
│   │       ├── ArchDiagram.tsx  # Architecture graph
│   │       ├── DependencyTree.tsx
│   │       └── CodeViewer.tsx   # Side panel code view
│   │
│   ├── services/                # Business logic
│   │   ├── websocket.ts         # WebSocket client
│   │   ├── api.ts               # REST API calls (if needed)
│   │   └── storage.ts           # LocalStorage utilities
│   │
│   ├── store/                   # Zustand state
│   │   ├── flowStore.ts         # Flow View state
│   │   ├── teamStore.ts         # Team View state
│   │   ├── chatStore.ts         # Chat View state
│   │   └── blueprintStore.ts    # Blueprint View state
│   │
│   ├── types/                   # TypeScript types
│   │   ├── agent.ts
│   │   ├── task.ts
│   │   ├── crew.ts
│   │   └── events.ts
│   │
│   └── lib/                     # Utilities
│       ├── utils.ts             # Helper functions
│       └── constants.ts         # Constants
│
├── backend/                      # FastAPI Python backend
│   ├── main.py                  # FastAPI app entry
│   ├── config.py                # Configuration
│   ├── database.py              # SQLAlchemy setup
│   ├── models.py                # SQLModel models
│   ├── schemas.py               # Pydantic schemas
│   │
│   ├── api/                     # API routes
│   │   ├── websocket.py         # WebSocket endpoint
│   │   ├── crews.py             # Crew management
│   │   └── health.py            # Health check
│   │
│   ├── services/                # Business logic
│   │   ├── event_bus.py         # Event broadcasting
│   │   ├── crewai_service.py    # CrewAI integration
│   │   ├── langfuse_client.py   # Langfuse integration
│   │   ├── hydra_protocol.py    # Code obfuscation
│   │   └── task_queue.py        # Background tasks
│   │
│   ├── crews/                   # Predefined crews
│   │   ├── bug_hunter.py
│   │   ├── feature_developer.py
│   │   └── code_reviewer.py
│   │
│   └── tests/                   # Tests
│       ├── test_api.py
│       └── test_crews.py
│
├── .env.example                 # Environment variables template
├── package.json                 # Node.js dependencies
├── tsconfig.json                # TypeScript config
├── vite.config.ts               # Vite config
├── tailwind.config.js           # Tailwind config
├── README.md                    # Project documentation
└── .gitignore
```

---

## Phase 1: Foundation Setup

### Step 1.1: Initialize Tauri Project

```bash
# Install Tauri CLI
npm install -g @tauri-apps/cli

# Create new Tauri + React + TypeScript project
npm create tauri-app@latest

# Answers to prompts:
# - Project name: mw-vision
# - Package manager: npm
# - UI template: react-ts
# - Add: @tauri-apps/plugin-websocket

cd mw-vision
```

### Step 1.2: Configure Tauri

**File: `src-tauri/tauri.conf.json`**

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "MW-Vision",
  "version": "0.1.0",
  "identifier": "com.mindwarehouse.mw-vision",
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": ""
    }
  },
  "app": {
    "windows": [
      {
        "title": "MW-Vision",
        "width": 1400,
        "height": 900,
        "resizable": true,
        "fullscreen": false,
        "minWidth": 1024,
        "minHeight": 768
      }
    ],
    "security": {
      "csp": null
    },
    "trayIcon": {
      "iconPath": "icons/icon.png",
      "iconAsTemplate": true
    }
  },
  "plugins": {
    "websocket": {
      "scope": ["ws://localhost:*", "wss://localhost:*"]
    }
  }
}
```

### Step 1.3: Install Frontend Dependencies

```bash
# Core dependencies
npm install react react-dom
npm install @xyflow/react zustand recharts
npm install lucide-react class-variance-authority clsx tailwind-merge
npm install @tauri-apps/api @tauri-apps/plugin-websocket
npm install date-fns

# Dev dependencies
npm install -D @types/react @types/react-dom
npm install -D @vitejs/plugin-react typescript vite
npm install -D @tauri-apps/cli tailwindcss autoprefixer postcss
```

### Step 1.4: Setup Tailwind CSS

```bash
npx tailwindcss init -p
```

**File: `tailwind.config.js`**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
      },
    },
  },
  plugins: [],
}
```

**File: `src/index.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### Step 1.5: Setup Python Backend

```bash
# Create backend directory
mkdir backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn[standard] websockets
pip install sqlalchemy sqlmodel pydantic python-dotenv
pip install crewai langfuse agentops
pip install rich aiofiles

# Save requirements
pip freeze > requirements.txt
```

### Step 1.6: Environment Configuration

**File: `.env.example`**

```env
# API Keys
OPENROUTER_API_KEY=sk-or-v1-xxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
AGENTOPS_API_KEY=xxxxx

# Backend Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8765
DATABASE_URL=sqlite:///./mw-vision.db
LOG_LEVEL=INFO

# Langfuse
LANGFUSE_HOST=http://localhost:3000

# Feature Flags
ENABLE_HYDRA_PROTOCOL=true
ENABLE_MOBILE_PWA=false
```

---

## Phase 2: Core Backend

### Step 2.1: FastAPI Application Setup

**File: `backend/main.py`**

```python
"""
MW-Vision Backend - FastAPI Application
Main entry point for the FastAPI server running as Tauri sidecar.
"""
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

from database import create_db_and_tables
from api import websocket, health, crews
from services.event_bus import EventBus

load_dotenv()

# Global event bus instance
event_bus = EventBus()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    print("🚀 MW-Vision Backend starting...")
    create_db_and_tables()
    print("✅ Database initialized")
    
    # Start background tasks
    asyncio.create_task(event_bus.start())
    print("✅ Event bus started")
    
    yield
    
    # Shutdown
    print("🛑 MW-Vision Backend shutting down...")
    await event_bus.stop()
    print("✅ Cleanup complete")

app = FastAPI(
    title="MW-Vision Backend",
    description="Visual Command Center for AI Development",
    version="0.1.0",
    lifespan=lifespan
)

# CORS for Tauri frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "tauri://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(websocket.router, prefix="/api", tags=["websocket"])
app.include_router(crews.router, prefix="/api/crews", tags=["crews"])

# Make event_bus available to all modules
app.state.event_bus = event_bus

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("FASTAPI_HOST", "0.0.0.0"),
        port=int(os.getenv("FASTAPI_PORT", 8765)),
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
```

### Step 2.2: Database Models

**File: `backend/database.py`**

```python
"""Database configuration and session management."""
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./mw-vision.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for database sessions."""
    with Session(engine) as session:
        yield session
```

**File: `backend/models.py`**

```python
"""SQLModel database models."""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel, JSON, Column
from pydantic import BaseModel

class Task(SQLModel, table=True):
    """Represents a crew execution task."""
    id: Optional[int] = Field(default=None, primary_key=True)
    crew_name: str = Field(index=True)
    status: str = Field(default="pending")  # pending, running, completed, failed
    context: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    total_cost: float = Field(default=0.0)
    total_time: float = Field(default=0.0)  # seconds
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Agent(SQLModel, table=True):
    """Represents an AI agent in a crew."""
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id", index=True)
    role: str
    model: str
    status: str = Field(default="idle")  # idle, thinking, completed, failed
    output: Optional[str] = None
    tokens_used: int = Field(default=0)
    cost: float = Field(default=0.0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Event(SQLModel, table=True):
    """Stores event log for audit trail."""
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", index=True)
    event_type: str = Field(index=True)
    data: Dict[str, Any] = Field(sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### Step 2.3: Event Bus

**File: `backend/services/event_bus.py`**

```python
"""
Event Bus for broadcasting events to all connected WebSocket clients.
"""
import asyncio
from typing import Dict, Any, Set
from fastapi import WebSocket
from datetime import datetime

class EventBus:
    """Manages event broadcasting to WebSocket clients."""
    
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
    
    async def start(self):
        """Start the event bus processor."""
        self.running = True
        asyncio.create_task(self._process_events())
    
    async def stop(self):
        """Stop the event bus."""
        self.running = False
    
    async def _process_events(self):
        """Process events from queue and broadcast to clients."""
        while self.running:
            try:
                event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
                await self._broadcast(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")
    
    async def emit(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to all connected clients."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.event_queue.put(event)
    
    async def _broadcast(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients."""
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send_json(event)
            except Exception:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
    
    def add_client(self, websocket: WebSocket):
        """Add a WebSocket client."""
        self.clients.add(websocket)
    
    def remove_client(self, websocket: WebSocket):
        """Remove a WebSocket client."""
        self.clients.discard(websocket)
```

### Step 2.4: WebSocket Endpoint

**File: `backend/api/websocket.py`**

```python
"""WebSocket endpoint for real-time communication."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
import json

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, request: Request):
    """Main WebSocket endpoint for frontend communication."""
    await websocket.accept()
    
    event_bus = request.app.state.event_bus
    event_bus.add_client(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection.established",
            "data": {"message": "Connected to MW-Vision backend"},
            "timestamp": ""
        })
        
        # Listen for messages from client
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            # Handle different message types
            action = data.get("action")
            
            if action == "launch_crew":
                await handle_launch_crew(websocket, data, request)
            elif action == "stop_crew":
                await handle_stop_crew(websocket, data, request)
            elif action == "ping":
                await websocket.send_json({"type": "pong", "data": {}})
            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": f"Unknown action: {action}"}
                })
    
    except WebSocketDisconnect:
        event_bus.remove_client(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        event_bus.remove_client(websocket)

async def handle_launch_crew(websocket: WebSocket, data: dict, request: Request):
    """Handle crew launch request."""
    from services.crewai_service import launch_crew_async
    
    crew_name = data.get("crew")
    context = data.get("context", {})
    
    # Launch crew in background
    task_id = await launch_crew_async(crew_name, context, request.app.state.event_bus)
    
    await websocket.send_json({
        "type": "crew.launched",
        "data": {"task_id": task_id, "crew_name": crew_name}
    })

async def handle_stop_crew(websocket: WebSocket, data: dict, request: Request):
    """Handle crew stop request."""
    task_id = data.get("task_id")
    
    # TODO: Implement crew stopping logic
    
    await websocket.send_json({
        "type": "crew.stopped",
        "data": {"task_id": task_id}
    })
```

### Step 2.5: CrewAI Integration Service

**File: `backend/services/crewai_service.py`**

```python
"""
CrewAI integration service.
Manages crew creation, execution, and event emission.
"""
import asyncio
from typing import Dict, Any
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from langfuse.callback import CallbackHandler
import os

from database import engine
from models import Task as TaskModel, Agent as AgentModel
from sqlmodel import Session, select

async def launch_crew_async(crew_name: str, context: Dict[str, Any], event_bus) -> int:
    """Launch a crew asynchronously."""
    # Create task record
    with Session(engine) as session:
        task = TaskModel(
            crew_name=crew_name,
            status="initializing",
            context=context
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        task_id = task.id
    
    # Emit event
    await event_bus.emit("task.created", {
        "task_id": task_id,
        "crew_name": crew_name,
        "status": "initializing"
    })
    
    # Run crew in background
    asyncio.create_task(_run_crew(task_id, crew_name, context, event_bus))
    
    return task_id

async def _run_crew(task_id: int, crew_name: str, context: Dict[str, Any], event_bus):
    """Execute crew (runs in background)."""
    try:
        # Update status
        with Session(engine) as session:
            task = session.get(TaskModel, task_id)
            task.status = "running"
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
        
        await event_bus.emit("task.started", {"task_id": task_id})
        
        # Get crew definition
        crew = get_crew_by_name(crew_name, context, event_bus, task_id)
        
        # Execute (this will block, but we're in asyncio task so it's OK)
        result = await asyncio.to_thread(crew.kickoff)
        
        # Update task with result
        with Session(engine) as session:
            task = session.get(TaskModel, task_id)
            task.status = "completed"
            task.result = {"output": str(result)}
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
        
        await event_bus.emit("task.completed", {
            "task_id": task_id,
            "result": str(result)
        })
    
    except Exception as e:
        # Update task with error
        with Session(engine) as session:
            task = session.get(TaskModel, task_id)
            task.status = "failed"
            task.result = {"error": str(e)}
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
        
        await event_bus.emit("task.failed", {
            "task_id": task_id,
            "error": str(e)
        })

def get_crew_by_name(crew_name: str, context: Dict[str, Any], event_bus, task_id: int) -> Crew:
    """Get crew definition by name."""
    if crew_name == "bug_hunter":
        from crews.bug_hunter import create_bug_hunting_crew
        return create_bug_hunting_crew(context, event_bus, task_id)
    else:
        raise ValueError(f"Unknown crew: {crew_name}")
```

### Step 2.6: Example Crew Implementation

**File: `backend/crews/bug_hunter.py`**

```python
"""Bug Hunting Crew - investigates and resolves bugs."""
from crewai import Agent, Task, Crew, Process
from services.event_bus import EventBus

def create_bug_hunting_crew(context: dict, event_bus: EventBus, task_id: int) -> Crew:
    """Create bug hunting crew."""
    
    # Custom callback to emit events
    class EventEmittingCallback:
        def __init__(self, agent_role: str):
            self.agent_role = agent_role
        
        def on_agent_start(self, *args, **kwargs):
            import asyncio
            asyncio.create_task(event_bus.emit("agent.started", {
                "task_id": task_id,
                "agent_role": self.agent_role,
                "model": kwargs.get("model", "unknown")
            }))
        
        def on_agent_end(self, *args, **kwargs):
            import asyncio
            asyncio.create_task(event_bus.emit("agent.completed", {
                "task_id": task_id,
                "agent_role": self.agent_role,
                "output": str(kwargs.get("output", ""))
            }))
    
    architect = Agent(
        role="Software Architect",
        goal="Analyze bug and generate root cause hypotheses",
        backstory="Expert with 30 years experience finding architectural issues.",
        llm="openrouter/anthropic/claude-sonnet-4-5",
        verbose=True,
        callbacks=[EventEmittingCallback("Architect")]
    )
    
    debugger = Agent(
        role="Expert Debugger",
        goal="Reproduce bug and confirm root cause",
        backstory="Specialist in debugging production systems.",
        llm="openrouter/anthropic/claude-sonnet-4-5",
        verbose=True,
        callbacks=[EventEmittingCallback("Debugger")]
    )
    
    bug_description = context.get("bug_description", "Unknown bug")
    file_path = context.get("file_path", "")
    
    task_analyze = Task(
        description=f"""Analyze this bug: {bug_description}
        File: {file_path}
        Generate 3+ hypotheses ordered by probability.""",
        agent=architect,
        expected_output="3+ prioritized hypotheses"
    )
    
    task_debug = Task(
        description="Investigate hypotheses and confirm root cause. Propose fix with code.",
        agent=debugger,
        expected_output="Root cause + proposed fix",
        context=[task_analyze]
    )
    
    crew = Crew(
        agents=[architect, debugger],
        tasks=[task_analyze, task_debug],
        process=Process.sequential,
        verbose=True
    )
    
    return crew
```

---

## Phase 3: Frontend Implementation

### Step 3.1: React Entry Point

**File: `src/main.tsx`**

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**File: `src/App.tsx`**

```typescript
import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import FlowView from './components/flow/FlowView'
import TeamView from './components/team/TeamView'
import ChatView from './components/chat/ChatView'
import BlueprintView from './components/blueprint/BlueprintView'
import { Network, Users, MessageSquare, FileCode } from 'lucide-react'

export default function App() {
  const [activeTab, setActiveTab] = useState<string>("flow")

  return (
    <div className="h-screen w-screen bg-background text-foreground overflow-hidden">
      <div className="flex flex-col h-full">
        {/* Header */}
        <header className="border-b border-border px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <Network className="w-5 h-5 text-primary-foreground" />
              </div>
              <h1 className="text-xl font-bold">MW-Vision</h1>
            </div>
            <div className="text-sm text-muted-foreground">
              Command Center for AI Development
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-4 border-b border-border rounded-none h-14">
              <TabsTrigger value="flow" className="gap-2">
                <Network className="w-4 h-4" />
                Flow View
              </TabsTrigger>
              <TabsTrigger value="team" className="gap-2">
                <Users className="w-4 h-4" />
                Team View
              </TabsTrigger>
              <TabsTrigger value="chat" className="gap-2">
                <MessageSquare className="w-4 h-4" />
                Chat View
              </TabsTrigger>
              <TabsTrigger value="blueprint" className="gap-2">
                <FileCode className="w-4 h-4" />
                Blueprint
              </TabsTrigger>
            </TabsList>

            <div className="flex-1 overflow-hidden">
              <TabsContent value="flow" className="h-full m-0 p-0">
                <FlowView />
              </TabsContent>
              <TabsContent value="team" className="h-full m-0 p-0">
                <TeamView />
              </TabsContent>
              <TabsContent value="chat" className="h-full m-0 p-0">
                <ChatView />
              </TabsContent>
              <TabsContent value="blueprint" className="h-full m-0 p-0">
                <BlueprintView />
              </TabsContent>
            </div>
          </Tabs>
        </main>
      </div>
    </div>
  )
}
```

### Step 3.2: WebSocket Service

**File: `src/services/websocket.ts`**

```typescript
/**
 * WebSocket service for real-time communication with backend
 */

type EventHandler = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private eventHandlers: Map<string, Set<EventHandler>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(url: string = 'ws://localhost:8765/api/ws') {
    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connection', { status: 'connected' })
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          const { type, data } = message

          // Emit to all handlers registered for this event type
          const handlers = this.eventHandlers.get(type)
          if (handlers) {
            handlers.forEach(handler => handler(data))
          }

          // Also emit to wildcard handlers
          const wildcardHandlers = this.eventHandlers.get('*')
          if (wildcardHandlers) {
            wildcardHandlers.forEach(handler => handler({ type, data }))
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', { error })
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.emit('connection', { status: 'disconnected' })
        this.attemptReconnect(url)
      }
    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
      this.attemptReconnect(url)
    }
  }

  private attemptReconnect(url: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => this.connect(url), this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnect attempts reached')
    }
  }

  send(action: string, data: any = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action, ...data }))
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  on(eventType: string, handler: EventHandler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, new Set())
    }
    this.eventHandlers.get(eventType)!.add(handler)
  }

  off(eventType: string, handler: EventHandler) {
    const handlers = this.eventHandlers.get(eventType)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  private emit(eventType: string, data: any) {
    const handlers = this.eventHandlers.get(eventType)
    if (handlers) {
      handlers.forEach(handler => handler(data))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Singleton instance
export const wsService = new WebSocketService()
```

### Step 3.3: Zustand Stores

**File: `src/store/flowStore.ts`**

```typescript
import { create } from 'zustand'
import { Node, Edge } from '@xyflow/react'

interface FlowState {
  nodes: Node[]
  edges: Edge[]
  addNode: (node: Node) => void
  updateNode: (nodeId: string, data: Partial<Node['data']>) => void
  addEdge: (edge: Edge) => void
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
}

export const useFlowStore = create<FlowState>((set) => ({
  nodes: [],
  edges: [],
  
  addNode: (node) => set((state) => ({
    nodes: [...state.nodes, node]
  })),
  
  updateNode: (nodeId, data) => set((state) => ({
    nodes: state.nodes.map((node) =>
      node.id === nodeId
        ? { ...node, data: { ...node.data, ...data } }
        : node
    )
  })),
  
  addEdge: (edge) => set((state) => ({
    edges: [...state.edges, edge]
  })),
  
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
}))
```

**File: `src/store/teamStore.ts`**

```typescript
import { create } from 'zustand'

interface Agent {
  id: string
  role: string
  model: string
  status: 'idle' | 'thinking' | 'completed' | 'failed'
  currentTask?: string
  tokensUsed: number
  cost: number
  elapsedTime: number
}

interface TeamState {
  agents: Agent[]
  totalCost: number
  addAgent: (agent: Agent) => void
  updateAgent: (agentId: string, updates: Partial<Agent>) => void
  incrementCost: (amount: number) => void
}

export const useTeamStore = create<TeamState>((set) => ({
  agents: [],
  totalCost: 0,
  
  addAgent: (agent) => set((state) => ({
    agents: [...state.agents, agent]
  })),
  
  updateAgent: (agentId, updates) => set((state) => ({
    agents: state.agents.map((agent) =>
      agent.id === agentId
        ? { ...agent, ...updates }
        : agent
    )
  })),
  
  incrementCost: (amount) => set((state) => ({
    totalCost: state.totalCost + amount
  })),
}))
```

### Step 3.4: Flow View Component

**File: `src/components/flow/FlowView.tsx`**

```typescript
import { useCallback, useEffect } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import CustomNode from './CustomNode'
import { wsService } from '../../services/websocket'
import { useFlowStore } from '../../store/flowStore'

const nodeTypes = {
  custom: CustomNode,
}

export default function FlowView() {
  const { nodes: storeNodes, edges: storeEdges, setNodes, setEdges } = useFlowStore()
  
  const [nodes, , onNodesChange] = useNodesState(storeNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  )

  // Listen for WebSocket events to update nodes
  useEffect(() => {
    const handleTaskCreated = (data: any) => {
      const newNode = {
        id: `task-${data.task_id}`,
        type: 'custom',
        position: { x: 100, y: 100 },
        data: {
          label: data.crew_name,
          status: 'initializing',
          taskId: data.task_id,
        },
      }
      setNodes([...nodes, newNode])
    }

    const handleAgentStarted = (data: any) => {
      const agentNode = {
        id: `agent-${data.agent_role}-${data.task_id}`,
        type: 'custom',
        position: { x: 300, y: 100 },
        data: {
          label: data.agent_role,
          status: 'thinking',
          model: data.model,
        },
      }
      setNodes([...nodes, agentNode])
    }

    wsService.on('task.created', handleTaskCreated)
    wsService.on('agent.started', handleAgentStarted)

    return () => {
      wsService.off('task.created', handleTaskCreated)
      wsService.off('agent.started', handleAgentStarted)
    }
  }, [nodes, setNodes])

  // Connect to WebSocket on mount
  useEffect(() => {
    wsService.connect()
    return () => wsService.disconnect()
  }, [])

  return (
    <div className="w-full h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}
```

**File: `src/components/flow/CustomNode.tsx`**

```typescript
import { memo } from 'react'
import { Handle, Position, NodeProps } from '@xyflow/react'
import { Card } from '../ui/card'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react'

function CustomNode({ data }: NodeProps) {
  const getStatusIcon = () => {
    switch (data.status) {
      case 'thinking':
        return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />
    }
  }

  const getStatusColor = () => {
    switch (data.status) {
      case 'thinking':
        return 'border-blue-500'
      case 'completed':
        return 'border-green-500'
      case 'failed':
        return 'border-red-500'
      default:
        return 'border-yellow-500'
    }
  }

  return (
    <Card className={`p-4 min-w-[200px] border-2 ${getStatusColor()}`}>
      <Handle type="target" position={Position.Top} />
      
      <div className="flex items-start gap-2">
        {getStatusIcon()}
        <div className="flex-1">
          <div className="font-semibold text-sm">{data.label}</div>
          {data.model && (
            <div className="text-xs text-muted-foreground mt-1">
              {data.model}
            </div>
          )}
          {data.cost !== undefined && (
            <div className="text-xs text-muted-foreground mt-1">
              Cost: ${data.cost.toFixed(4)}
            </div>
          )}
        </div>
      </div>
      
      <Handle type="source" position={Position.Bottom} />
    </Card>
  )
}

export default memo(CustomNode)
```

### Step 3.5: Team View Component

**File: `src/components/team/TeamView.tsx`**

```typescript
import { useEffect } from 'react'
import AgentCard from './AgentCard'
import { useTeamStore } from '../../store/teamStore'
import { wsService } from '../../services/websocket'

export default function TeamView() {
  const { agents, totalCost } = useTeamStore()

  useEffect(() => {
    const handleAgentStarted = (data: any) => {
      useTeamStore.getState().addAgent({
        id: `${data.agent_role}-${data.task_id}`,
        role: data.agent_role,
        model: data.model,
        status: 'thinking',
        tokensUsed: 0,
        cost: 0,
        elapsedTime: 0,
      })
    }

    const handleAgentCompleted = (data: any) => {
      useTeamStore.getState().updateAgent(`${data.agent_role}-${data.task_id}`, {
        status: 'completed',
      })
    }

    wsService.on('agent.started', handleAgentStarted)
    wsService.on('agent.completed', handleAgentCompleted)

    return () => {
      wsService.off('agent.started', handleAgentStarted)
      wsService.off('agent.completed', handleAgentCompleted)
    }
  }, [])

  return (
    <div className="h-full overflow-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Team Dashboard</h2>
        <p className="text-muted-foreground">
          Total Cost: ${totalCost.toFixed(4)}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      {agents.length === 0 && (
        <div className="text-center text-muted-foreground mt-12">
          No active agents. Launch a crew to get started.
        </div>
      )}
    </div>
  )
}
```

**File: `src/components/team/AgentCard.tsx`**

```typescript
import { Card } from '../ui/card'
import { Loader2, CheckCircle2, XCircle, Clock } from 'lucide-react'

interface Agent {
  id: string
  role: string
  model: string
  status: 'idle' | 'thinking' | 'completed' | 'failed'
  currentTask?: string
  tokensUsed: number
  cost: number
  elapsedTime: number
}

interface AgentCardProps {
  agent: Agent
}

export default function AgentCard({ agent }: AgentCardProps) {
  const getStatusIcon = () => {
    switch (agent.status) {
      case 'thinking':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />
    }
  }

  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        {getStatusIcon()}
        <div className="flex-1">
          <h3 className="font-semibold">{agent.role}</h3>
          <p className="text-sm text-muted-foreground">{agent.model}</p>
          
          {agent.currentTask && (
            <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
              {agent.currentTask}
            </p>
          )}

          <div className="mt-3 space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Tokens:</span>
              <span>{agent.tokensUsed.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Cost:</span>
              <span>${agent.cost.toFixed(4)}</span>
            </div>
            {agent.elapsedTime > 0 && (
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">Time:</span>
                <span>{Math.floor(agent.elapsedTime)}s</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
```

### Step 3.6: Chat View Component

**File: `src/components/chat/ChatView.tsx`**

```typescript
import { useState, useRef, useEffect } from 'react'
import { Card } from '../ui/card'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Send } from 'lucide-react'
import { wsService } from '../../services/websocket'

interface Message {
  id: string
  type: 'user' | 'system'
  content: string
  timestamp: Date
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to MW-Vision. Type a command to get started.',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    const handleCrewLaunched = (data: any) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'system',
          content: `✅ Launched ${data.crew_name} crew (Task #${data.task_id})`,
          timestamp: new Date(),
        },
      ])
    }

    const handleTaskCompleted = (data: any) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'system',
          content: `✅ Task #${data.task_id} completed.\n\n${data.result}`,
          timestamp: new Date(),
        },
      ])
    }

    wsService.on('crew.launched', handleCrewLaunched)
    wsService.on('task.completed', handleTaskCompleted)

    return () => {
      wsService.off('crew.launched', handleCrewLaunched)
      wsService.off('task.completed', handleTaskCompleted)
    }
  }, [])

  const handleSend = () => {
    if (!input.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])

    // Parse command and send to backend
    parseAndExecuteCommand(input)

    setInput('')
  }

  const parseAndExecuteCommand = (command: string) => {
    const lowerCmd = command.toLowerCase()

    if (lowerCmd.includes('run') && lowerCmd.includes('bug')) {
      wsService.send('launch_crew', {
        crew: 'bug_hunter',
        context: {
          bug_description: command,
          file_path: '',
        },
      })
    } else {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: 'system',
          content: `I don't understand that command yet. Try: "Run bug hunting crew on network_analysis.py"`,
          timestamp: new Date(),
        },
      ])
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <Card
              className={`p-4 max-w-2xl ${
                msg.type === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              <p className="text-xs opacity-70 mt-2">
                {msg.timestamp.toLocaleTimeString()}
              </p>
            </Card>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border p-4">
        <div className="flex gap-2">
          <Input
            placeholder="Type a command... e.g., 'Run bug hunting crew'"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <Button onClick={handleSend} size="icon">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
```

### Step 3.7: Blueprint View Placeholder

**File: `src/components/blueprint/BlueprintView.tsx`**

```typescript
import { Card } from '../ui/card'

export default function BlueprintView() {
  return (
    <div className="h-full p-6">
      <Card className="p-8 text-center">
        <h2 className="text-2xl font-bold mb-4">Blueprint View</h2>
        <p className="text-muted-foreground">
          System architecture visualization will be implemented in Phase 4.
        </p>
        <p className="text-muted-foreground mt-2">
          This view will show module dependencies, code classification, and tech stack.
        </p>
      </Card>
    </div>
  )
}
```

---

## Phase 4: Integration & Testing

### Step 4.1: Connect Frontend to Backend

1. **Start Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8765
```

2. **Start Frontend (Tauri Dev):**
```bash
npm run tauri dev
```

3. **Test WebSocket Connection:**
   - Open MW-Vision desktop app
   - Check browser DevTools console for "✅ WebSocket connected"
   - Go to Chat View
   - Type: "Run bug hunting crew"
   - Verify event flow in Team View and Flow View

### Step 4.2: Testing Checklist

**Manual Tests:**
- [ ] App launches without errors
- [ ] All 4 views are accessible via tabs
- [ ] WebSocket connects to backend
- [ ] Chat command launches crew
- [ ] Flow View shows new nodes
- [ ] Team View shows agent cards
- [ ] Agents update status in real-time
- [ ] Cost tracking increments
- [ ] Completion event triggers notification

**Automated Tests (Optional but Recommended):**

**File: `backend/tests/test_api.py`**

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_websocket_connection():
    with client.websocket_connect("/api/ws") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connection.established"
```

---

## Phase 5: Mobile & Security

### Step 5.1: Progressive Web App Setup

**File: `public/manifest.json`**

```json
{
  "name": "MW-Vision",
  "short_name": "MW-Vision",
  "description": "Visual Command Center for AI Development",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#09090b",
  "theme_color": "#3b82f6",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

**File: `vite.config.ts` (add PWA plugin)**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'MW-Vision',
        short_name: 'MW-Vision',
        theme_color: '#3b82f6',
      },
    }),
  ],
})
```

### Step 5.2: Tailscale Integration (Manual Setup)

1. **Install Tailscale** on PC: https://tailscale.com/download
2. **Install Tailscale** on mobile
3. **Start Backend** with `--host 0.0.0.0`
4. **Access from Mobile:**
   - Get Tailscale IP: `tailscale ip -4`
   - Open in mobile browser: `http://100.x.x.x:8765`

### Step 5.3: Hydra Protocol Implementation

**File: `backend/services/hydra_protocol.py`**

```python
"""Hydra Protocol - Code obfuscation for IP protection."""
import re
import hashlib
import random
from typing import List, Dict

class HydraObfuscator:
    """Obfuscates code before sending to untrusted models."""
    
    def __init__(self):
        self.mapping: Dict[str, str] = {}
    
    def obfuscate(self, code: str, sensitive_names: List[str]) -> str:
        """Obfuscate sensitive identifiers in code."""
        obfuscated = code
        
        for name in sensitive_names:
            fake_name = self._generate_fake_name()
            self.mapping[fake_name] = name
            obfuscated = re.sub(r'\b' + re.escape(name) + r'\b', fake_name, obfuscated)
        
        # Remove comments
        obfuscated = re.sub(r'#.*$', '', obfuscated, flags=re.MULTILINE)
        obfuscated = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '""""""', obfuscated)
        
        return obfuscated
    
    def deobfuscate(self, code: str) -> str:
        """Restore original names."""
        result = code
        for fake_name, real_name in self.mapping.items():
            result = re.sub(r'\b' + re.escape(fake_name) + r'\b', real_name, result)
        return result
    
    def _generate_fake_name(self) -> str:
        """Generate random but valid Python identifier."""
        prefix = random.choice(['var', 'func', 'obj', 'item', 'data'])
        suffix = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        return f"{prefix}_{suffix}"
```

---

## Phase 6: Deployment

### Step 6.1: Build for Production

```bash
# Build frontend + Tauri app
npm run tauri build

# Output locations:
# Windows: src-tauri/target/release/mw-vision.exe
# macOS: src-tauri/target/release/bundle/dmg/
# Linux: src-tauri/target/release/bundle/appimage/
```

### Step 6.2: Python Backend Distribution

**Option A: Bundle with PyInstaller**

```bash
pip install pyinstaller

pyinstaller --onefile \
    --hidden-import=crewai \
    --hidden-import=langfuse \
    backend/main.py
```

**Option B: Embed as Tauri Sidecar**

Update `tauri.conf.json`:

```json
{
  "bundle": {
    "externalBin": ["backend/dist/main"]
  }
}
```

### Step 6.3: Distribution

**Windows:**
- Create installer with Inno Setup or NSIS
- Sign with code signing certificate (optional)
- Distribute via website download

**macOS:**
- Sign and notarize DMG with Apple Developer account
- Distribute via website or Mac App Store

**Linux:**
- AppImage for universal compatibility
- Flatpak/Snap for distribution via app stores

---

## Appendices

### Appendix A: Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| WebSocket won't connect | Check backend is running on port 8765, check firewall |
| React Flow nodes not rendering | Verify @xyflow/react CSS is imported |
| Tauri window blank | Check Vite dev server is running on port 5173 |
| CrewAI import errors | Ensure virtual environment is activated |

### Appendix B: Performance Optimization

- Use React.memo for expensive components
- Virtualize long lists (react-window)
- Debounce WebSocket events if >10/sec
- Use Zustand selectors to prevent unnecessary re-renders

### Appendix C: Security Best Practices

- Never commit .env files
- Validate all WebSocket messages
- Sanitize user input in Chat View
- Use Hydra Protocol for sensitive code
- Implement rate limiting on backend

### Appendix D: Further Reading

- Tauri Docs: https://v2.tauri.app
- React Flow: https://reactflow.dev
- CrewAI: https://docs.crewai.com
- Langfuse: https://langfuse.com/docs
- FastAPI: https://fastapi.tiangolo.com

---

## Conclusion

This technical specification provides a complete, step-by-step guide to implementing MW-Vision. Follow each phase sequentially, test thoroughly, and refer to the appendices for troubleshooting.

**Estimated Timeline:**
- Phase 1: 3 days
- Phase 2: 5 days
- Phase 3: 10 days
- Phase 4: 3 days
- Phase 5: 4 days
- Phase 6: 3 days

**Total: ~4 weeks** for experienced developer, ~6 weeks for AI agent with validation.

---

**Document Control:**
- Version: 1.0
- Last Updated: February 13, 2026
- Maintainer: Technical Team
