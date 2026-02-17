# MW-VISION RESTORATION MISSION
## Prompt for Claude CLI (Field Commander)

**Mission ID:** MW-VISION-RESTORE-001  
**Date:** February 17, 2026  
**Project Location:** `L:\nicedev-Project\MW-Vision\mw-vision-app`  
**Objective:** Transform MW-Vision from mock-data showcase into functional MoE monitoring dashboard  
**Executor:** Claude CLI (Autonomous)  
**Supervisor:** Victor Hernandez (Supreme Commander, MindWarehouse)

---

## MISSION CONTEXT

You are Field Commander executing a critical restoration of MW-Vision, MindWarehouse's flagship dashboard for visualizing Mixture of Experts (MoE) AI orchestration. The current implementation is **visually complete but functionally hollow** - all data is hardcoded mock values.

**Your mission:** Convert this beautiful shell into a working command center with real data flowing through WebSocket connections, Strategic Coordinator decision-making visible, and actual agent operations tracked.

---

## STRATEGIC BACKGROUND

### What is MindWarehouse?
- AI orchestration platform with proprietary MoE routing logic
- **Key differentiator:** "One Step Ahead" - intelligent model selection (Haiku vs Sonnet) based on complexity analysis
- **Cost optimization:** Documented 74-94% savings vs all-Sonnet approach
- **Primary use case:** OSINT-MW (Venezuela intelligence operations for potential ICC prosecution)

### What is MW-Vision?
- Real-time monitoring dashboard for MoE operations
- **Purpose:** Make Strategic Coordinator routing decisions visible
- **Target users:** Victor (during deliveries), intelligence analysts, enterprise clients
- **Original concept:** Like Palantir Foundry but for MindWarehouse's AI workflows

### Current State (CRITICAL UNDERSTANDING)
The application you're working on has:
- ✅ **Complete UI:** React + TypeScript + Vite, professionally designed
- ✅ **4 functional views:** Flow View, Team View, Chat View, Blueprint View
- ✅ **Visual polish:** Cyberpunk aesthetic, smooth animations, responsive layout
- ❌ **Zero real data:** All metrics hardcoded, Response Time always 0.0s
- ❌ **No backend:** Only Vite dev server on port 5189
- ❌ **Strategic Coordinator missing:** Core concept not implemented visually
- ❌ **Mock WebSocket:** Simulates connections but sends fake data

---

## EVIDENCE OF CURRENT STATE

### Screenshot Analysis (5 images provided to you separately)

**Image 1 - Flow View (Initial State):**
```
Visible elements:
├─ Header: "MW-VISION - Visual Command Center for AI Agents - ONE STEP AHEAD"
├─ Status badges: Security, Alpha Test, CONNECTED
├─ Cost display: $0.0000 / $10 (4 decimals - WRONG FORMAT)
├─ Estimated Cost: $3.00 (hardcoded)
├─ Tabs: Flow View, Team View, Chat View, Blueprint View
├─ Buttons: Launch Crew, Pause All, Reset
├─ Agent Flow Canvas:
│   ├─ Debugger (claude-3-5-sonnet) - Cost: $0.00
│   ├─ Code Reviewer (deepseek-chat) - Cost: $0.00
│   └─ Test Generator (gpt-4o) - Cost: $0.00
└─ Mini-map (bottom right): Shows gray/green bars
```

**Problem identified:** No Strategic Coordinator node visible. Canvas mostly empty.

**Image 2 - Flow View (After "Launch Crew" clicked):**
```
Changes from Image 1:
├─ Cost display: $4.5600 / $10 (still 4 decimals)
├─ "Total Cost Accumulated" label appears: $4.56
├─ Agent costs updated:
│   ├─ Debugger: $0.98
│   ├─ Code Reviewer: $1.97
│   └─ Test Generator: $1.61
├─ Status: RUNNING (green badge in header)
└─ Mini-map bars changed to green
```

**Problem identified:** Costs updated instantly (impossible in real execution). No progressive updates. Math is correct ($0.98 + $1.97 + $1.61 = $4.56) but timing is suspicious.

**Image 3 - Team View:**
```
Top metrics:
├─ Active Agents: 3 of 3 running
├─ Total Tasks: 0 (No tasks yet) ← CONTRADICTION
├─ Total Cost: $4.56 (Accumulated cost)
└─ Avg Response: 0.0s ← SMOKING GUN

Agent Status Cards:
├─ Debugger
│   ├─ Model: claude-3-5-sonnet
│   ├─ Status: RUNNING (green badge)
│   ├─ Tasks Completed: 0 ← CONTRADICTION with RUNNING
│   ├─ Cost: $0.9800 (4 decimals)
│   ├─ Response Time: 0.0s ← IMPOSSIBLE
│   └─ Last Update: 3:08:32 PM
├─ Code Reviewer
│   ├─ Model: deepseek-chat
│   ├─ Status: RUNNING
│   ├─ Tasks Completed: 0
│   ├─ Cost: $1.9700
│   ├─ Response Time: 0.0s
│   └─ Last Update: 3:08:32 PM
└─ Test Generator
    ├─ Model: gpt-4o
    ├─ Status: RUNNING
    ├─ Tasks Completed: 0
    ├─ Cost: $1.6100
    ├─ Response Time: 0.0s
    └─ Last Update: 3:08:32 PM
```

**Problems identified:**
1. Status = RUNNING but Tasks Completed = 0 (logical impossibility)
2. Response Time = 0.0s for ALL agents (physically impossible)
3. Cost has accumulated but no tasks completed (how?)
4. Last Update identical for all agents (3:08:32 PM - static timestamp)
5. Cost format inconsistent (4 decimals: $0.9800 instead of $0.98)

**Image 4 - Chat View:**
```
Title: Natural Language Command Interface
Status: Running, Cost: $4.5600
Content:
├─ Welcome message: "Welcome to MW-Vision Command Interface..."
├─ Command input box (empty)
└─ Quick Commands:
    ├─ Launch Crew (Start all agents)
    ├─ Pause Crew (Stop all agents)
    ├─ Status (View crew status)
    └─ Cost Check (View spending)
```

**Problem identified:** No message history. No routing decisions logged. Should be renamed to "Mission Log" and show Strategic Coordinator activity.

**Image 5 - Blueprint View:**
```
Top stats:
├─ Total Files: 4
├─ Proprietary: 2
├─ Public: 2
└─ Hydra Protected: 0

GitHub Repository Import section
Code Classification:
├─ src/auth/login.ts - 234 lines - PROPRIETARY
├─ src/utils/helpers.ts - 89 lines - PUBLIC
├─ src/api/endpoints.ts - 423 lines - PROPRIETARY
└─ src/components/Button.tsx - 67 lines - PUBLIC

Hydra Protocol v2 (STANDBY):
├─ Fragmentation: Code split into chunks
├─ Steganography: Hidden markers in comments
└─ Schema Rotation: Every ~50 requests
```

**Problem identified:** These file paths look fake (generic names). No GitHub integration actually implemented.

---

## TECHNICAL EVIDENCE FROM DOCUMENTATION

### MW-VISION-HIGH-AVAILABILITY.md Analysis
```
Current Status:
- Vite dev server running on port 5189
- No mention of backend server
- No WebSocket server running
- Document focuses on FUTURE high availability (PM2, Docker, NSSM)
```

**Conclusion:** This is planning for infrastructure that doesn't exist yet. Classic cart-before-horse.

---

## YOUR MISSION OBJECTIVES (PRIORITY ORDER)

### PHASE 1: BACKEND FOUNDATION (CRITICAL)
**Goal:** Create real backend that serves actual data  
**Duration:** 4-6 hours  
**Status:** NOT STARTED

#### Task 1.1: Create Python FastAPI Backend
**Why:** Currently there's no backend at all. Vite dev server (port 5189) is just serving the React app.

**Implementation steps:**

1. **Create backend directory structure:**
```bash
cd L:\nicedev-Project\MW-Vision
mkdir -p backend/src
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install fastapi uvicorn websockets pydantic python-dotenv anthropic openai --upgrade
pip freeze > requirements.txt
```

4. **Create `backend/src/main.py`:**
```python
"""
MW-Vision Backend Server
Real-time telemetry for MoE operations
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import random
import uuid

# Agent state management
class Agent:
    def __init__(self, id: str, name: str, model: str):
        self.id = id
        self.name = name
        self.model = model
        self.status = "idle"  # idle, running, paused, error
        self.tasks_completed = 0
        self.total_cost = 0.0
        self.last_response_time = 0.0
        self.last_update = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "status": self.status,
            "tasksCompleted": self.tasks_completed,
            "totalCost": round(self.total_cost, 4),
            "lastResponseTime": round(self.last_response_time, 2),
            "lastUpdate": self.last_update
        }

# Initialize agents
agents: Dict[str, Agent] = {
    "debugger": Agent("debugger", "Debugger", "claude-3-5-sonnet"),
    "code-reviewer": Agent("code-reviewer", "Code Reviewer", "deepseek-chat"),
    "test-generator": Agent("test-generator", "Test Generator", "gpt-4o")
}

# Strategic Coordinator decisions
routing_history: List[dict] = []

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WebSocket] Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)

manager = ConnectionManager()

# Background task: Simulate agent activity
async def simulate_agent_activity():
    """
    Background task that simulates MoE operations
    In real implementation, this would listen to actual agent events
    """
    while True:
        await asyncio.sleep(10)  # Every 10 seconds
        
        # Randomly pick an agent to "execute" a task
        agent_id = random.choice(list(agents.keys()))
        agent = agents[agent_id]
        
        # Simulate Strategic Coordinator routing decision
        complexity = random.randint(1, 10)
        should_use_haiku = complexity < 5
        
        decision = {
            "timestamp": datetime.now().isoformat(),
            "query": f"Simulated task #{agent.tasks_completed + 1}",
            "complexity": complexity,
            "selectedModel": "claude-3-haiku" if should_use_haiku else agent.model,
            "reasoning": (
                f"Low complexity ({complexity}/10) - routing to Haiku for cost efficiency"
                if should_use_haiku
                else f"High complexity ({complexity}/10) - routing to {agent.model} for quality"
            ),
            "estimatedCost": 0.001 if should_use_haiku else 0.01
        }
        
        routing_history.append(decision)
        
        # Update agent status
        agent.status = "running"
        agent.last_update = datetime.now().isoformat()
        
        await manager.broadcast({
            "type": "agent_status_changed",
            "agent": agent.to_dict()
        })
        
        await manager.broadcast({
            "type": "routing_decision",
            "decision": decision
        })
        
        # Simulate execution time
        execution_time = random.uniform(0.5, 2.5)  # 0.5 to 2.5 seconds
        await asyncio.sleep(execution_time)
        
        # Task completed
        actual_cost = decision["estimatedCost"] * random.uniform(0.8, 1.2)  # ±20% variance
        
        agent.tasks_completed += 1
        agent.total_cost += actual_cost
        agent.last_response_time = execution_time
        agent.status = "idle"
        agent.last_update = datetime.now().isoformat()
        
        await manager.broadcast({
            "type": "task_completed",
            "agent": agent.to_dict(),
            "decision": decision,
            "actualCost": round(actual_cost, 4),
            "responseTime": round(execution_time, 2)
        })

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    task = asyncio.create_task(simulate_agent_activity())
    print("[Backend] Background task started")
    yield
    # Shutdown
    task.cancel()
    print("[Backend] Background task stopped")

# FastAPI app
app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5189", "http://127.0.0.1:5189"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API Endpoints
@app.get("/")
async def root():
    return {"status": "MW-Vision Backend Online", "version": "1.0.0"}

@app.get("/api/agents")
async def get_agents():
    """Get all agents status"""
    return [agent.to_dict() for agent in agents.values()]

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent status"""
    if agent_id not in agents:
        return {"error": "Agent not found"}, 404
    return agents[agent_id].to_dict()

@app.post("/api/agents/{agent_id}/execute")
async def execute_task(agent_id: str, task: dict):
    """Execute a task on specific agent"""
    if agent_id not in agents:
        return {"error": "Agent not found"}, 404
    
    agent = agents[agent_id]
    
    # Simulate Strategic Coordinator routing
    complexity = random.randint(1, 10)
    should_use_haiku = complexity < 5
    
    decision = {
        "timestamp": datetime.now().isoformat(),
        "query": task.get("task", "Manual execution"),
        "complexity": complexity,
        "selectedModel": "claude-3-haiku" if should_use_haiku else agent.model,
        "reasoning": (
            f"Low complexity ({complexity}/10) - routing to Haiku"
            if should_use_haiku
            else f"High complexity ({complexity}/10) - routing to {agent.model}"
        ),
        "estimatedCost": 0.001 if should_use_haiku else 0.01
    }
    
    routing_history.append(decision)
    
    # Update status
    agent.status = "running"
    agent.last_update = datetime.now().isoformat()
    
    await manager.broadcast({
        "type": "agent_status_changed",
        "agent": agent.to_dict()
    })
    
    await manager.broadcast({
        "type": "routing_decision",
        "decision": decision
    })
    
    # Simulate execution
    execution_time = random.uniform(0.5, 2.5)
    await asyncio.sleep(execution_time)
    
    # Complete task
    actual_cost = decision["estimatedCost"] * random.uniform(0.8, 1.2)
    
    agent.tasks_completed += 1
    agent.total_cost += actual_cost
    agent.last_response_time = execution_time
    agent.status = "idle"
    agent.last_update = datetime.now().isoformat()
    
    await manager.broadcast({
        "type": "task_completed",
        "agent": agent.to_dict(),
        "decision": decision,
        "actualCost": round(actual_cost, 4),
        "responseTime": round(execution_time, 2)
    })
    
    return {
        "success": True,
        "agent": agent.to_dict(),
        "decision": decision,
        "actualCost": round(actual_cost, 4),
        "responseTime": round(execution_time, 2)
    }

@app.get("/api/routing-history")
async def get_routing_history():
    """Get recent routing decisions"""
    return routing_history[-50:]  # Last 50 decisions

@app.get("/api/stats")
async def get_stats():
    """Get overall statistics"""
    total_cost = sum(agent.total_cost for agent in agents.values())
    total_tasks = sum(agent.tasks_completed for agent in agents.values())
    active_agents = sum(1 for agent in agents.values() if agent.status == "running")
    
    # Calculate savings vs all-Sonnet
    avg_sonnet_cost = 0.01
    all_sonnet_cost = total_tasks * avg_sonnet_cost
    savings = all_sonnet_cost - total_cost
    
    return {
        "totalCost": round(total_cost, 4),
        "totalTasks": total_tasks,
        "activeAgents": active_agents,
        "savings": round(savings, 4),
        "allSonnetCost": round(all_sonnet_cost, 4)
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time updates"""
    await manager.connect(websocket)
    
    # Send initial state
    await websocket.send_text(json.dumps({
        "type": "initial_state",
        "agents": [agent.to_dict() for agent in agents.values()],
        "routingHistory": routing_history[-10:]
    }))
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back (for ping/pong)
            await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("MW-VISION BACKEND STARTING")
    print("=" * 60)
    print(f"REST API: http://localhost:8000")
    print(f"WebSocket: ws://localhost:8000/ws")
    print(f"Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
```

5. **Test backend:**
```bash
cd L:\nicedev-Project\MW-Vision\backend
.\venv\Scripts\activate
python src/main.py
```

**Expected output:**
```
============================================================
MW-VISION BACKEND STARTING
============================================================
REST API: http://localhost:8000
WebSocket: ws://localhost:8000/ws
Docs: http://localhost:8000/docs
============================================================
INFO:     Started server process [XXXX]
INFO:     Uvicorn running on http://0.0.0.0:8000
[Backend] Background task started
```

6. **Verify endpoints work:**
```bash
# In another terminal:
curl http://localhost:8000/api/agents
curl http://localhost:8000/api/stats
```

Should return JSON with agent data.

**Validation criteria:**
- ✅ Backend starts without errors
- ✅ `/api/agents` returns 3 agents
- ✅ `/api/stats` returns valid statistics
- ✅ Background task logs appear every 10 seconds

---

#### Task 1.2: Connect Frontend to Real Backend
**Why:** Frontend currently has hardcoded data. Must fetch from actual API.

**Implementation steps:**

1. **Update API base URL in frontend:**

Find file: `mw-vision-app/src/services/api.ts` or similar

Change:
```typescript
// OLD (if it exists):
const API_BASE = 'http://localhost:5189/api';  // Wrong, this is Vite

// NEW:
const API_BASE = 'http://localhost:8000/api';  // Actual backend
```

2. **Create/Update WebSocket hook:**

File: `mw-vision-app/src/hooks/useWebSocket.ts`

```typescript
import { useEffect, useRef, useState } from 'react';

const WS_URL = 'ws://localhost:8000/ws';

export function useWebSocket(onMessage: (data: any) => void) {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const reconnectTimeout = useRef<NodeJS.Timeout>();

  useEffect(() => {
    function connect() {
      console.log('[WebSocket] Connecting to', WS_URL);
      ws.current = new WebSocket(WS_URL);

      ws.current.onopen = () => {
        console.log('[WebSocket] Connected');
        setConnected(true);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('[WebSocket] Message received:', data.type);
          onMessage(data);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      ws.current.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setConnected(false);
        
        // Auto-reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(() => {
          console.log('[WebSocket] Reconnecting...');
          connect();
        }, 5000);
      };

      ws.current.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
      };
    }

    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [onMessage]);

  return { connected };
}
```

3. **Update Team View to use real data:**

Find the Team View component (likely `src/components/TeamView.tsx` or `src/views/TeamView.tsx`)

Add at the top:
```typescript
import { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Agent {
  id: string;
  name: string;
  model: string;
  status: 'idle' | 'running' | 'paused' | 'error';
  tasksCompleted: number;
  totalCost: number;
  lastResponseTime: number;
  lastUpdate: string;
}

export function TeamView() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  // Initial load from API
  useEffect(() => {
    fetch('http://localhost:8000/api/agents')
      .then(res => res.json())
      .then(data => {
        setAgents(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load agents:', err);
        setLoading(false);
      });
  }, []);

  // Real-time updates via WebSocket
  useWebSocket((message) => {
    if (message.type === 'agent_status_changed') {
      setAgents(prev => prev.map(a => 
        a.id === message.agent.id ? message.agent : a
      ));
    } else if (message.type === 'task_completed') {
      setAgents(prev => prev.map(a => 
        a.id === message.agent.id ? message.agent : a
      ));
    } else if (message.type === 'initial_state') {
      setAgents(message.agents);
    }
  });

  if (loading) {
    return <div>Loading agents...</div>;
  }

  // Rest of the component...
}
```

4. **Format costs correctly (2 decimals everywhere):**

Create utility file: `src/utils/formatters.ts`

```typescript
export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}

export function formatResponseTime(seconds: number): string {
  if (seconds === 0) return '0.0s';
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
  return `${seconds.toFixed(2)}s`;
}
```

Then replace all cost displays:
```typescript
// OLD:
<div>Cost: ${agent.totalCost}</div>

// NEW:
import { formatCost } from '../utils/formatters';
<div>Cost: {formatCost(agent.totalCost)}</div>
```

**Validation criteria:**
- ✅ Frontend fetches agents on load
- ✅ WebSocket connects (check browser console for "WebSocket Connected")
- ✅ Response Times show real values (0.5s - 2.5s)
- ✅ Costs formatted as $X.XX (2 decimals)
- ✅ When backend simulates a task, frontend updates automatically

---

### PHASE 2: STRATEGIC COORDINATOR VISUALIZATION (HIGH PRIORITY)
**Goal:** Show the Strategic Coordinator as central decision-maker  
**Duration:** 2-3 hours  
**Status:** NOT STARTED

#### Task 2.1: Add Strategic Coordinator Node to Flow View

**Implementation:**

1. **Find the Flow View component** (likely uses React Flow library)

Look for file with imports like:
```typescript
import ReactFlow, { Node, Edge } from 'reactflow';
```

2. **Add Strategic Coordinator as central node:**

```typescript
const strategicCoordinatorNode: Node = {
  id: 'strategic-coordinator',
  type: 'special', // or create custom node type
  position: { x: 400, y: 150 }, // Center position
  data: {
    label: 'Strategic Coordinator',
    subtitle: 'Claude Desktop',
    role: 'decision-maker',
    icon: '🧠', // Brain emoji
    style: {
      background: 'linear-gradient(135deg, #00d9ff, #ff006e)',
      border: '3px solid #00d9ff',
      borderRadius: '12px',
      padding: '20px',
      fontSize: '16px',
      fontWeight: 'bold',
      color: '#ffffff',
      boxShadow: '0 0 30px rgba(0, 217, 255, 0.6)',
      minWidth: '200px',
      textAlign: 'center'
    }
  }
};
```

3. **Add edges showing routing decisions:**

```typescript
const routingEdges: Edge[] = [
  {
    id: 'sc-to-debugger',
    source: 'strategic-coordinator',
    target: 'debugger',
    label: 'Complexity < 5 → Haiku',
    animated: true,
    style: { stroke: '#39ff14', strokeWidth: 2 }
  },
  {
    id: 'sc-to-code-reviewer',
    source: 'strategic-coordinator',
    target: 'code-reviewer',
    label: 'Complexity ≥ 5 → Sonnet',
    animated: true,
    style: { stroke: '#ff006e', strokeWidth: 2 }
  },
  {
    id: 'sc-to-test-generator',
    source: 'strategic-coordinator',
    target: 'test-generator',
    label: 'Complexity ≥ 7 → GPT-4',
    animated: true,
    style: { stroke: '#ffbe0b', strokeWidth: 2 }
  }
];
```

4. **Reposition existing nodes around SC:**

```typescript
const agentNodes: Node[] = [
  {
    id: 'debugger',
    position: { x: 150, y: 350 }, // Bottom left
    // ... rest of debugger node config
  },
  {
    id: 'code-reviewer',
    position: { x: 650, y: 350 }, // Bottom right
    // ... rest of code-reviewer node config
  },
  {
    id: 'test-generator',
    position: { x: 400, y: 500 }, // Bottom center
    // ... rest of test-generator node config
  }
];

const allNodes = [strategicCoordinatorNode, ...agentNodes];
```

**Validation criteria:**
- ✅ Strategic Coordinator node appears in center of canvas
- ✅ Has distinct visual style (gradient background, glow effect)
- ✅ Edges connect SC to all agents
- ✅ Edge labels show routing logic

---

#### Task 2.2: Show Routing Decisions in Real-Time

**Implementation:**

Create new component: `src/components/RoutingDecisionsPanel.tsx`

```typescript
import { useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface RoutingDecision {
  timestamp: string;
  query: string;
  complexity: number;
  selectedModel: string;
  reasoning: string;
  estimatedCost: number;
}

export function RoutingDecisionsPanel() {
  const [decisions, setDecisions] = useState<RoutingDecision[]>([]);

  // Load initial history
  useEffect(() => {
    fetch('http://localhost:8000/api/routing-history')
      .then(res => res.json())
      .then(data => setDecisions(data.slice(-10))) // Last 10
      .catch(console.error);
  }, []);

  // Listen for new decisions
  useWebSocket((message) => {
    if (message.type === 'routing_decision') {
      setDecisions(prev => [message.decision, ...prev].slice(0, 10));
    }
  });

  return (
    <div style={{
      position: 'absolute',
      top: '80px',
      right: '20px',
      width: '350px',
      maxHeight: '500px',
      background: 'rgba(18, 24, 41, 0.95)',
      border: '1px solid #00d9ff',
      borderRadius: '8px',
      padding: '15px',
      overflowY: 'auto',
      zIndex: 1000
    }}>
      <h3 style={{
        color: '#00d9ff',
        fontSize: '16px',
        marginBottom: '15px',
        fontFamily: 'Orbitron, monospace'
      }}>
        Strategic Coordinator Decisions
      </h3>
      
      {decisions.map((decision, i) => (
        <div key={i} style={{
          borderLeft: `3px solid ${decision.complexity < 5 ? '#39ff14' : '#ff006e'}`,
          padding: '10px',
          marginBottom: '10px',
          background: 'rgba(0, 0, 0, 0.3)',
          borderRadius: '4px'
        }}>
          <div style={{ fontSize: '10px', color: '#8892a6' }}>
            {new Date(decision.timestamp).toLocaleTimeString()}
          </div>
          <div style={{ fontSize: '13px', color: '#e0e6ed', marginTop: '5px' }}>
            {decision.query.substring(0, 50)}...
          </div>
          <div style={{ fontSize: '12px', color: '#00d9ff', marginTop: '5px' }}>
            Complexity: {decision.complexity}/10 → {decision.selectedModel}
          </div>
          <div style={{ fontSize: '11px', color: '#8892a6', marginTop: '5px' }}>
            {decision.reasoning}
          </div>
        </div>
      ))}
    </div>
  );
}
```

Add this component to Flow View:
```typescript
// In FlowView.tsx
import { RoutingDecisionsPanel } from './RoutingDecisionsPanel';

return (
  <div style={{ position: 'relative', width: '100%', height: '100%' }}>
    <ReactFlow nodes={nodes} edges={edges} />
    <RoutingDecisionsPanel />
  </div>
);
```

**Validation criteria:**
- ✅ Panel appears on right side of Flow View
- ✅ Shows last 10 routing decisions
- ✅ Updates in real-time when backend makes decisions
- ✅ Color-coded by complexity (green = Haiku, red = Sonnet/GPT-4)

---

### PHASE 3: MISSION LOG (MEDIUM PRIORITY)
**Goal:** Convert Chat View into Mission Log showing all operations  
**Duration:** 2 hours  
**Status:** NOT STARTED

#### Task 3.1: Rename Chat View to Mission Log

**Implementation:**

1. **Rename component file:**
```bash
cd L:\nicedev-Project\MW-Vision\mw-vision-app\src
# Find the Chat component
# Rename ChatView.tsx to MissionLog.tsx (or similar)
```

2. **Update tab label:**

Find where tabs are defined (usually in main App or Layout component):
```typescript
// OLD:
<Tab icon={ChatIcon}>Chat View</Tab>

// NEW:
<Tab icon={TerminalIcon}>Mission Log</Tab>
```

3. **Redesign component to show operation logs:**

```typescript
// src/components/MissionLog.tsx
import { useEffect, useState, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface LogEntry {
  timestamp: string;
  type: 'decision' | 'execution' | 'completion' | 'system';
  message: string;
  data?: any;
}

export function MissionLog() {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      timestamp: new Date().toISOString(),
      type: 'system',
      message: '✓ MW-Vision Mission Control initialized'
    }
  ]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useWebSocket((message) => {
    const timestamp = new Date().toISOString();
    
    if (message.type === 'routing_decision') {
      const decision = message.decision;
      setLogs(prev => [...prev, {
        timestamp,
        type: 'decision',
        message: `SC: Query complexity ${decision.complexity}/10 → Routing to ${decision.selectedModel}`,
        data: decision
      }]);
    }
    
    if (message.type === 'agent_status_changed' && message.agent.status === 'running') {
      setLogs(prev => [...prev, {
        timestamp,
        type: 'execution',
        message: `${message.agent.name}: Executing task...`,
        data: message.agent
      }]);
    }
    
    if (message.type === 'task_completed') {
      setLogs(prev => [...prev, {
        timestamp,
        type: 'completion',
        message: `${message.agent.name}: ✓ Completed in ${message.responseTime}s - Cost: $${message.actualCost.toFixed(4)}`,
        data: message
      }]);
    }
  });

  // Auto-scroll to bottom
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogStyle = (type: string) => {
    switch (type) {
      case 'decision':
        return { borderLeftColor: '#00d9ff', color: '#00d9ff' };
      case 'execution':
        return { borderLeftColor: '#ffbe0b', color: '#ffbe0b' };
      case 'completion':
        return { borderLeftColor: '#39ff14', color: '#39ff14' };
      case 'system':
        return { borderLeftColor: '#8892a6', color: '#8892a6' };
      default:
        return { borderLeftColor: '#e0e6ed', color: '#e0e6ed' };
    }
  };

  return (
    <div style={{
      width: '100%',
      height: '100%',
      background: '#0a0e1a',
      padding: '20px',
      overflowY: 'auto',
      fontFamily: "'Share Tech Mono', monospace"
    }}>
      <div style={{
        marginBottom: '20px',
        paddingBottom: '10px',
        borderBottom: '1px solid rgba(0, 217, 255, 0.3)'
      }}>
        <h2 style={{
          color: '#00d9ff',
          fontSize: '20px',
          fontFamily: "'Orbitron', monospace",
          marginBottom: '5px'
        }}>
          Mission Log
        </h2>
        <p style={{
          color: '#8892a6',
          fontSize: '12px',
          letterSpacing: '1px'
        }}>
          Strategic Coordinator Activity Feed
        </p>
      </div>

      {logs.map((log, i) => {
        const style = getLogStyle(log.type);
        return (
          <div key={i} style={{
            borderLeft: `3px solid ${style.borderLeftColor}`,
            padding: '10px 15px',
            marginBottom: '10px',
            background: 'rgba(0, 0, 0, 0.3)',
            borderRadius: '4px',
            fontSize: '13px',
            lineHeight: '1.6'
          }}>
            <span style={{ color: '#8892a6', fontSize: '11px' }}>
              [{new Date(log.timestamp).toLocaleTimeString()}]
            </span>
            {' '}
            <span style={{ color: style.color }}>
              {log.message}
            </span>
          </div>
        );
      })}
      
      <div ref={logEndRef} />
    </div>
  );
}
```

**Validation criteria:**
- ✅ Tab renamed from "Chat View" to "Mission Log"
- ✅ Shows system initialization message
- ✅ Logs routing decisions in cyan
- ✅ Logs task execution in yellow
- ✅ Logs completions in green
- ✅ Auto-scrolls to show latest logs

---

### PHASE 4: DATA CONSISTENCY (LOW PRIORITY BUT EASY)
**Goal:** Fix formatting inconsistencies  
**Duration:** 1 hour  
**Status:** NOT STARTED

#### Task 4.1: Standardize All Cost Displays

**Implementation:**

1. **Use formatters everywhere:**

Search for all instances of cost display:
```bash
cd L:\nicedev-Project\MW-Vision\mw-vision-app
grep -r "\$\${" src/ --include="*.tsx" --include="*.ts"
```

Replace all with:
```typescript
import { formatCost } from '../utils/formatters';

// OLD patterns:
// ${cost}
// ${cost.toFixed(4)}
// $${totalCost}

// NEW:
{formatCost(cost)}
```

2. **Fix header cost display:**

Find header component, change:
```typescript
// OLD:
Cost: ${currentCost} / $10

// NEW:
Cost: {formatCost(currentCost)} / {formatCost(budget)}
```

**Validation criteria:**
- ✅ All costs show exactly 2 decimals: $2.47, not $2.4700
- ✅ Header shows "Cost: $4.56 / $10.00"
- ✅ Agent cards show costs like $0.98, $1.97

---

#### Task 4.2: Fix Agent Status Logic

**Why:** Agents show "RUNNING" with 0 tasks completed - illogical.

**Implementation:**

Agent status should be determined by backend. Frontend just displays it.

The backend already sets status correctly:
- `idle` when not working
- `running` during execution

Frontend just needs to display it correctly:

```typescript
function getStatusBadge(status: string) {
  const styles = {
    running: { bg: '#39ff14', text: '#000', label: 'RUNNING' },
    idle: { bg: '#8892a6', text: '#000', label: 'IDLE' },
    paused: { bg: '#ffbe0b', text: '#000', label: 'PAUSED' },
    error: { bg: '#ff006e', text: '#fff', label: 'ERROR' }
  };
  
  const style = styles[status] || styles.idle;
  
  return (
    <span style={{
      background: style.bg,
      color: style.text,
      padding: '4px 12px',
      borderRadius: '12px',
      fontSize: '11px',
      fontWeight: 'bold'
    }}>
      {style.label}
    </span>
  );
}
```

**Validation criteria:**
- ✅ Agents show "IDLE" when no tasks active
- ✅ Agents show "RUNNING" only during actual execution
- ✅ Status updates in real-time via WebSocket

---

## VERIFICATION PROTOCOL

After completing each phase, you MUST verify it works before proceeding.

### Verification Checklist

**Phase 1 Verification:**
```bash
# Terminal 1: Start backend
cd L:\nicedev-Project\MW-Vision\backend
.\venv\Scripts\activate
python src/main.py
# Should show: "MW-VISION BACKEND STARTING"

# Terminal 2: Test API
curl http://localhost:8000/api/agents
# Should return JSON array with 3 agents

# Terminal 3: Start frontend
cd L:\nicedev-Project\MW-Vision\mw-vision-app
npm run dev
# Should show: "Local: http://localhost:5189"

# Browser:
# Open http://localhost:5189
# Open DevTools (F12) → Console tab
# Should see: "[WebSocket] Connected"
# Go to Team View
# Verify: Response Times show real values (not 0.0s)
# Verify: Tasks Completed increments over time
```

**Phase 2 Verification:**
```bash
# Browser: Flow View
# Should see:
# - Strategic Coordinator node in center
# - Edges connecting SC to agents
# - Routing Decisions panel on right
# - When backend simulates task, new decision appears
```

**Phase 3 Verification:**
```bash
# Browser: Mission Log tab
# Should see:
# - Tab renamed from "Chat View"
# - System initialization message
# - Real-time logs appearing when tasks execute
# - Color-coded by type (cyan, yellow, green)
```

**Phase 4 Verification:**
```bash
# Browser: All views
# Check header: Cost shows $X.XX format
# Check Team View: All costs show 2 decimals
# Check agent status: Shows IDLE when not working
```

---

## ANTI-HALLUCINATION MEASURES

### Rule 1: NEVER Assume Files Exist
If you're unsure where a file is:
```bash
cd L:\nicedev-Project\MW-Vision
find . -name "TeamView.tsx" -o -name "FlowView.tsx"
```

### Rule 2: ALWAYS Test Code Before Claiming Success
Don't say "I've updated X" without running it.

### Rule 3: Show Me Diffs for Critical Changes
For important file modifications, show:
```
File: src/components/TeamView.tsx
Lines changed: 45-60

OLD:
const agents = MOCK_AGENTS;

NEW:
const [agents, setAgents] = useState<Agent[]>([]);
useEffect(() => {
  fetch('http://localhost:8000/api/agents')
    .then(res => res.json())
    .then(setAgents);
}, []);
```

### Rule 4: Backend MUST Run Successfully
Before saying "backend is done", verify:
```bash
python src/main.py
# Must start without errors
# Must respond to curl http://localhost:8000/api/agents
```

---

## SUCCESS CRITERIA (Final Report)

At the end, provide a report showing:

```markdown
# MW-VISION RESTORATION REPORT

## PHASE 1: BACKEND FOUNDATION ✅ / ❌
- [x] Task 1.1: Backend created and running
  - Evidence: `python src/main.py` output shows no errors
  - Evidence: `curl http://localhost:8000/api/agents` returns JSON
- [x] Task 1.2: Frontend connected to backend
  - Evidence: Browser console shows "[WebSocket] Connected"
  - Evidence: Team View shows Response Times > 0.0s

## PHASE 2: STRATEGIC COORDINATOR ✅ / ❌
- [x] Task 2.1: SC node added to Flow View
  - Evidence: Screenshot showing central node
  - Evidence: Edges connecting SC to agents
- [x] Task 2.2: Routing decisions panel
  - Evidence: Panel visible on right side
  - Evidence: Decisions update in real-time

## PHASE 3: MISSION LOG ✅ / ❌
- [x] Task 3.1: Chat renamed to Mission Log
  - Evidence: Tab shows "Mission Log"
  - Evidence: Logs show routing decisions

## PHASE 4: DATA CONSISTENCY ✅ / ❌
- [x] Task 4.1: Cost formatting standardized
  - Evidence: All costs show $X.XX format
- [x] Task 4.2: Agent status logic fixed
  - Evidence: Agents show IDLE when not working

## FILES CREATED
- backend/src/main.py
- backend/requirements.txt
- mw-vision-app/src/hooks/useWebSocket.ts
- mw-vision-app/src/components/RoutingDecisionsPanel.tsx
- mw-vision-app/src/components/MissionLog.tsx
- mw-vision-app/src/utils/formatters.ts

## FILES MODIFIED
- mw-vision-app/src/services/api.ts (changed API_BASE)
- mw-vision-app/src/components/TeamView.tsx (connected to real API)
- mw-vision-app/src/components/FlowView.tsx (added SC node)
- [List all other modified files]

## EVIDENCE
[Attach screenshots showing:]
1. Backend running without errors
2. Flow View with Strategic Coordinator
3. Mission Log with real-time logs
4. Team View with real Response Times
```

---

## YOUR COMMUNICATION PROTOCOL

**During execution:**
- Update Victor after completing each task
- If you encounter an error, show the full error message
- If you're unsure about something, ASK before proceeding

**Format for updates:**
```
[TASK 1.1] Creating backend...
✓ Virtual environment created
✓ Dependencies installed
✓ main.py created
⚠ Testing backend startup...
✓ Backend running on port 8000
✓ API endpoints responding
[TASK 1.1 COMPLETE]
```

**If you encounter problems:**
```
[TASK 1.2] ERROR
File: src/components/TeamView.tsx not found
Searched:
- src/components/TeamView.tsx
- src/views/TeamView.tsx
- src/pages/TeamView.tsx

REQUEST: Please provide the correct path or share the component location.
```

---

## FINAL INSTRUCTIONS

1. **Read this entire prompt carefully**
2. **Start with Phase 1, Task 1.1**
3. **Verify each task works before moving to the next**
4. **Provide the final report when all phases complete**
5. **If you get stuck, ask for help immediately**

**Remember:** The goal is not speed. The goal is a working product where:
- Backend serves real data
- Frontend displays real data
- Strategic Coordinator is visible
- Mission Log shows operations
- Costs are formatted correctly

Take your time. Verify everything. Show your work.

---

**Mission begins now.**

**ONE STEP AHEAD.**

---

END OF PROMPT
