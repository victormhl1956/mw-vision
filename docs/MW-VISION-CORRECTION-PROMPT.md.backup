# MW-VISION CORRECTION PROMPT FOR AI-CODER
## Comprehensive Instructions for Project A.C.E.

**Document Version:** 1.0  
**Date:** February 16, 2026  
**Project Path:** `L:\nicedev-Project\MW-Vision\mw-vision-app`  
**Execution Mode:** Sequential, with validation after each phase  
**Expected Duration:** 8-12 hours (spread across 2-3 work sessions)

---

## CONTEXT FOR AI-CODER

You are correcting MW-Vision, a real-time dashboard for monitoring MindWarehouse's Mixture of Experts (MoE) AI orchestration platform. The current implementation has diverged from the original design concept and uses mock data throughout.

**Original Concept:**
- Strategic Coordinator (Claude Desktop) makes intelligent routing decisions
- MoE routing: Haiku (fast/cheap) vs Sonnet (quality/expensive)
- Field Commanders (Claudia CLI) execute tasks
- OSINT-MW operations for Venezuela intelligence
- Real-time cost optimization visualization

**Current State:**
- Generic agent orchestrator (not MoE-specific)
- All data is mocked (Response Time = 0.0s, Tasks = 0)
- Strategic Coordinator concept absent from UI
- No real backend connections
- Hydra Protocol over-engineered

**Your Mission:**
Restore the original vision while maintaining the good technical architecture. Connect real data, implement Strategic Coordinator visualization, and demonstrate actual MoE routing.

---

## CRITICAL RULES

### 1. NO HALLUCINATIONS
- If you don't know the exact file path, USE `find` or `ls` to locate it
- If an API endpoint doesn't exist, CREATE a mock server first
- If you're unsure about syntax, CHECK the existing codebase
- NEVER assume a function exists - verify first

### 2. VALIDATION PROTOCOL
After EACH phase:
1. Run `npm run dev` to ensure no build errors
2. Open browser to `http://localhost:5189`
3. Take a screenshot or describe what you see
4. Verify the specific feature you implemented works
5. Report status in the format specified at the end

### 3. FILE SAFETY
- BACKUP before modifying: `cp file.tsx file.tsx.backup`
- Use version control: `git add -A && git commit -m "Phase X: Description"`
- If unsure, show me the diff before applying

### 4. DEPENDENCY INSTALLATION
Before using ANY new library:
```bash
npm install <package> --save
# OR for dev dependencies
npm install <package> --save-dev
```

---

## PHASE 1: CRITICAL FIXES (Impact: 10/10)
**Goal:** Connect real data and restore Strategic Coordinator concept  
**Duration:** 3-4 hours

### Task 1.1: Create Mock Backend Server
**Why:** Currently all data is hardcoded. We need a server that simulates real MoE operations.

**Implementation:**

1. **Create backend directory:**
```bash
cd L:\nicedev-Project\MW-Vision
mkdir -p backend/src
cd backend
npm init -y
npm install express cors ws uuid --save
npm install @types/express @types/cors @types/ws @types/node typescript ts-node --save-dev
```

2. **Create `backend/src/server.ts`:**
```typescript
import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

app.use(cors());
app.use(express.json());

// State management
interface Agent {
  id: string;
  name: string;
  model: string;
  status: 'idle' | 'running' | 'paused';
  tasksCompleted: number;
  totalCost: number;
  lastResponseTime: number;
  lastUpdate: string;
}

const agents: Map<string, Agent> = new Map([
  ['debugger', {
    id: 'debugger',
    name: 'Debugger',
    model: 'claude-3-5-sonnet',
    status: 'idle',
    tasksCompleted: 0,
    totalCost: 0,
    lastResponseTime: 0,
    lastUpdate: new Date().toISOString()
  }],
  ['code-reviewer', {
    id: 'code-reviewer',
    name: 'Code Reviewer',
    model: 'deepseek-chat',
    status: 'idle',
    tasksCompleted: 0,
    totalCost: 0,
    lastResponseTime: 0,
    lastUpdate: new Date().toISOString()
  }],
  ['test-generator', {
    id: 'test-generator',
    name: 'Test Generator',
    model: 'gpt-4o',
    status: 'idle',
    tasksCompleted: 0,
    totalCost: 0,
    lastResponseTime: 0,
    lastUpdate: new Date().toISOString()
  }]
]);

// Strategic Coordinator state
interface RoutingDecision {
  timestamp: string;
  query: string;
  complexity: number;
  selectedModel: string;
  reasoning: string;
  estimatedCost: number;
}

const routingHistory: RoutingDecision[] = [];

// API Endpoints
app.get('/api/agents', (req, res) => {
  res.json(Array.from(agents.values()));
});

app.get('/api/agents/:id', (req, res) => {
  const agent = agents.get(req.params.id);
  if (agent) {
    res.json(agent);
  } else {
    res.status(404).json({ error: 'Agent not found' });
  }
});

app.post('/api/agents/:id/execute', async (req, res) => {
  const agent = agents.get(req.params.id);
  if (!agent) {
    return res.status(404).json({ error: 'Agent not found' });
  }

  const { task } = req.body;
  
  // Simulate Strategic Coordinator routing decision
  const complexity = Math.floor(Math.random() * 10) + 1;
  const shouldUseHaiku = complexity < 5;
  
  const decision: RoutingDecision = {
    timestamp: new Date().toISOString(),
    query: task,
    complexity,
    selectedModel: shouldUseHaiku ? 'claude-3-haiku' : agent.model,
    reasoning: shouldUseHaiku 
      ? `Low complexity (${complexity}/10) - routing to Haiku for cost efficiency`
      : `High complexity (${complexity}/10) - routing to ${agent.model} for quality`,
    estimatedCost: shouldUseHaiku ? 0.001 : 0.01
  };
  
  routingHistory.push(decision);
  
  // Update agent status
  agent.status = 'running';
  broadcastToClients({ type: 'agent_status', agent });
  
  // Simulate task execution
  const executionTime = Math.random() * 2000 + 500; // 500-2500ms
  
  setTimeout(() => {
    const responseTime = executionTime / 1000;
    const actualCost = decision.estimatedCost * (0.8 + Math.random() * 0.4); // ±20% variance
    
    agent.tasksCompleted++;
    agent.totalCost += actualCost;
    agent.lastResponseTime = responseTime;
    agent.lastUpdate = new Date().toISOString();
    agent.status = 'idle';
    
    broadcastToClients({ 
      type: 'task_completed', 
      agent,
      decision,
      actualCost,
      responseTime 
    });
    
    res.json({ 
      success: true, 
      agent,
      decision,
      actualCost,
      responseTime 
    });
  }, executionTime);
});

app.get('/api/routing-history', (req, res) => {
  res.json(routingHistory.slice(-50)); // Last 50 decisions
});

app.get('/api/stats', (req, res) => {
  const totalCost = Array.from(agents.values()).reduce((sum, a) => sum + a.totalCost, 0);
  const totalTasks = Array.from(agents.values()).reduce((sum, a) => sum + a.tasksCompleted, 0);
  const activeAgents = Array.from(agents.values()).filter(a => a.status === 'running').length;
  
  // Calculate savings vs all-Sonnet
  const avgSonnetCost = 0.01;
  const allSonnetCost = totalTasks * avgSonnetCost;
  const savings = allSonnetCost - totalCost;
  
  res.json({
    totalCost,
    totalTasks,
    activeAgents,
    savings,
    allSonnetCost
  });
});

// WebSocket for real-time updates
wss.on('connection', (ws) => {
  console.log('Client connected');
  
  // Send initial state
  ws.send(JSON.stringify({ 
    type: 'initial_state', 
    agents: Array.from(agents.values()),
    routingHistory: routingHistory.slice(-10)
  }));
  
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

function broadcastToClients(data: any) {
  wss.clients.forEach((client) => {
    if (client.readyState === 1) { // OPEN
      client.send(JSON.stringify(data));
    }
  });
}

// Start server
const PORT = 8080;
server.listen(PORT, () => {
  console.log(`MW-Vision Backend running on http://localhost:${PORT}`);
  console.log(`WebSocket server running on ws://localhost:${PORT}`);
});
```

3. **Create `backend/tsconfig.json`:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

4. **Create `backend/package.json` scripts:**
```json
{
  "scripts": {
    "dev": "ts-node src/server.ts",
    "build": "tsc",
    "start": "node dist/server.js"
  }
}
```

5. **Test backend:**
```bash
cd L:\nicedev-Project\MW-Vision\backend
npm run dev
```

**Validation:**
- Backend starts without errors
- Visit `http://localhost:8080/api/agents` - should return JSON array
- Visit `http://localhost:8080/api/stats` - should return stats object

---

### Task 1.2: Connect Frontend to Backend
**Why:** Replace mock data with real API calls

**Implementation:**

1. **Create API client: `mw-vision-app/src/services/api.ts`**
```typescript
const API_BASE = 'http://localhost:8080/api';

export interface Agent {
  id: string;
  name: string;
  model: string;
  status: 'idle' | 'running' | 'paused';
  tasksCompleted: number;
  totalCost: number;
  lastResponseTime: number;
  lastUpdate: string;
}

export interface RoutingDecision {
  timestamp: string;
  query: string;
  complexity: number;
  selectedModel: string;
  reasoning: string;
  estimatedCost: number;
}

export interface Stats {
  totalCost: number;
  totalTasks: number;
  activeAgents: number;
  savings: number;
  allSonnetCost: number;
}

export const api = {
  async getAgents(): Promise<Agent[]> {
    const response = await fetch(`${API_BASE}/agents`);
    if (!response.ok) throw new Error('Failed to fetch agents');
    return response.json();
  },

  async getAgent(id: string): Promise<Agent> {
    const response = await fetch(`${API_BASE}/agents/${id}`);
    if (!response.ok) throw new Error('Failed to fetch agent');
    return response.json();
  },

  async executeTask(agentId: string, task: string): Promise<any> {
    const response = await fetch(`${API_BASE}/agents/${agentId}/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task })
    });
    if (!response.ok) throw new Error('Failed to execute task');
    return response.json();
  },

  async getRoutingHistory(): Promise<RoutingDecision[]> {
    const response = await fetch(`${API_BASE}/routing-history`);
    if (!response.ok) throw new Error('Failed to fetch routing history');
    return response.json();
  },

  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE}/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  }
};
```

2. **Create WebSocket hook: `mw-vision-app/src/hooks/useWebSocket.ts`**
```typescript
import { useEffect, useRef, useState } from 'react';

const WS_URL = 'ws://localhost:8080';

export function useWebSocket(onMessage: (data: any) => void) {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [onMessage]);

  return { connected };
}
```

3. **Update Team View to use real data**

Find the Team View component (likely `src/components/TeamView.tsx` or similar) and modify it:

```typescript
import { useEffect, useState } from 'react';
import { api, Agent } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export function TeamView() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  // Initial load
  useEffect(() => {
    api.getAgents()
      .then(setAgents)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  // Real-time updates
  useWebSocket((data) => {
    if (data.type === 'agent_status') {
      setAgents(prev => prev.map(a => 
        a.id === data.agent.id ? data.agent : a
      ));
    } else if (data.type === 'task_completed') {
      setAgents(prev => prev.map(a => 
        a.id === data.agent.id ? data.agent : a
      ));
    } else if (data.type === 'initial_state') {
      setAgents(data.agents);
    }
  });

  if (loading) {
    return <div>Loading agents...</div>;
  }

  return (
    <div>
      {/* Render agents with REAL data */}
      {agents.map(agent => (
        <AgentCard 
          key={agent.id} 
          agent={agent}
          onExecute={(task) => api.executeTask(agent.id, task)}
        />
      ))}
    </div>
  );
}
```

**Validation:**
- Run both backend (`npm run dev` in backend folder)
- Run frontend (`npm run dev` in mw-vision-app folder)
- Open browser, go to Team View
- Response Time should show real values (0.5s - 2.5s)
- Click "View Details" or execute a test task
- Verify Tasks Completed increments
- Verify Cost updates

---

### Task 1.3: Add Strategic Coordinator Visualization
**Why:** This is the core differentiator of MindWarehouse - missing from current UI

**Implementation:**

1. **Add Strategic Coordinator node to Flow View**

Locate the Flow View component and add a central "Strategic Coordinator" node:

```typescript
// In FlowView component or wherever nodes are defined

const strategicCoordinatorNode = {
  id: 'strategic-coordinator',
  type: 'special', // Or create a custom node type
  position: { x: 400, y: 200 }, // Center position
  data: { 
    label: 'Strategic Coordinator',
    subtitle: 'Claude Desktop',
    role: 'decision-maker',
    decisions: 0, // Will be updated from backend
    style: {
      background: 'linear-gradient(135deg, #00d9ff, #ff006e)',
      border: '3px solid #00d9ff',
      padding: '20px',
      borderRadius: '12px',
      fontSize: '16px',
      fontWeight: 'bold',
      boxShadow: '0 0 30px rgba(0, 217, 255, 0.6)'
    }
  }
};

// Add edges showing routing decisions
const routingEdges = [
  {
    id: 'sc-to-debugger',
    source: 'strategic-coordinator',
    target: 'debugger',
    label: 'complexity < 5 → Haiku',
    animated: true,
    style: { stroke: '#39ff14' }
  },
  {
    id: 'sc-to-code-reviewer',
    source: 'strategic-coordinator',
    target: 'code-reviewer',
    label: 'complexity ≥ 5 → Sonnet',
    animated: true,
    style: { stroke: '#ff006e' }
  },
  // ... more edges
];
```

2. **Create Strategic Coordinator Info Panel**

Add a panel showing recent routing decisions:

```typescript
// Create new component: src/components/StrategicCoordinatorPanel.tsx

import { useEffect, useState } from 'react';
import { api, RoutingDecision } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export function StrategicCoordinatorPanel() {
  const [decisions, setDecisions] = useState<RoutingDecision[]>([]);

  useEffect(() => {
    api.getRoutingHistory()
      .then(setDecisions)
      .catch(console.error);
  }, []);

  useWebSocket((data) => {
    if (data.type === 'task_completed' && data.decision) {
      setDecisions(prev => [data.decision, ...prev].slice(0, 10));
    }
  });

  return (
    <div style={{
      position: 'absolute',
      top: '80px',
      right: '20px',
      width: '350px',
      background: 'rgba(18, 24, 41, 0.95)',
      border: '1px solid #00d9ff',
      borderRadius: '8px',
      padding: '15px',
      maxHeight: '400px',
      overflowY: 'auto'
    }}>
      <h3 style={{ color: '#00d9ff', marginBottom: '10px' }}>
        Strategic Coordinator Decisions
      </h3>
      {decisions.map((decision, i) => (
        <div key={i} style={{
          borderLeft: '3px solid ' + (decision.complexity < 5 ? '#39ff14' : '#ff006e'),
          padding: '8px',
          marginBottom: '8px',
          background: 'rgba(0,0,0,0.3)',
          borderRadius: '4px'
        }}>
          <div style={{ fontSize: '11px', color: '#8892a6' }}>
            {new Date(decision.timestamp).toLocaleTimeString()}
          </div>
          <div style={{ fontSize: '13px', color: '#e0e6ed', marginTop: '4px' }}>
            {decision.query.substring(0, 50)}...
          </div>
          <div style={{ fontSize: '12px', color: '#00d9ff', marginTop: '4px' }}>
            Complexity: {decision.complexity}/10 → {decision.selectedModel}
          </div>
          <div style={{ fontSize: '11px', color: '#8892a6', marginTop: '4px' }}>
            {decision.reasoning}
          </div>
        </div>
      ))}
    </div>
  );
}
```

3. **Add to Flow View**

```typescript
// In FlowView.tsx or main flow component

import { StrategicCoordinatorPanel } from './StrategicCoordinatorPanel';

// In the render:
return (
  <div style={{ position: 'relative', width: '100%', height: '100%' }}>
    <ReactFlow nodes={nodes} edges={edges} /* ... */ />
    <StrategicCoordinatorPanel />
  </div>
);
```

**Validation:**
- Strategic Coordinator node appears in center of Flow View
- Edges connect SC to agents
- SC Info Panel shows on the right
- When you execute a task, a new decision appears in SC panel
- Decision shows: timestamp, query, complexity, selected model, reasoning

---

## PHASE 2: MISSION LOG (Impact: 8/10)
**Goal:** Replace Chat View with Mission Log showing routing decisions  
**Duration:** 2 hours

### Task 2.1: Rename and Redesign Chat View

**Implementation:**

1. **Rename files and references:**
```bash
# Find the Chat View file
cd L:\nicedev-Project\MW-Vision\mw-vision-app
find src -name "*Chat*" -o -name "*chat*"

# Rename (example, adjust based on actual filename)
git mv src/components/ChatView.tsx src/components/MissionLog.tsx
```

2. **Update tab label:**

Find where tabs are defined (likely in main App.tsx or layout component):
```typescript
// Change from:
<Tab icon={ChatIcon}>Chat View</Tab>

// To:
<Tab icon={TerminalIcon}>Mission Log</Tab>
```

3. **Redesign MissionLog component:**

```typescript
// src/components/MissionLog.tsx

import { useEffect, useState, useRef } from 'react';
import { api, RoutingDecision } from '../services/api';
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
      message: 'MW-Vision Mission Control initialized'
    }
  ]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useWebSocket((data) => {
    let newLog: LogEntry | null = null;

    if (data.type === 'task_completed') {
      const decision = data.decision as RoutingDecision;
      
      // Add routing decision log
      setLogs(prev => [...prev, {
        timestamp: decision.timestamp,
        type: 'decision',
        message: `SC: Query complexity ${decision.complexity}/10 → Routing to ${decision.selectedModel}`,
        data: decision
      }]);

      // Add execution log
      setTimeout(() => {
        setLogs(prev => [...prev, {
          timestamp: new Date().toISOString(),
          type: 'execution',
          message: `${data.agent.name}: Executing task...`,
          data: { agentId: data.agent.id }
        }]);
      }, 100);

      // Add completion log
      setTimeout(() => {
        setLogs(prev => [...prev, {
          timestamp: new Date().toISOString(),
          type: 'completion',
          message: `${data.agent.name}: ✓ Completed in ${data.responseTime.toFixed(2)}s - Cost: $${data.actualCost.toFixed(4)}`,
          data: { 
            agentId: data.agent.id,
            cost: data.actualCost,
            responseTime: data.responseTime
          }
        }]);
      }, 200);
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
      background: 'rgba(10, 14, 26, 0.8)',
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

**Validation:**
- Tab label changed to "Mission Log"
- When you execute a task, you see 3 log entries:
  1. "SC: Query complexity X/10 → Routing to Y"
  2. "Agent: Executing task..."
  3. "Agent: ✓ Completed in Xs - Cost: $Y"
- Logs auto-scroll to bottom
- Color-coded by type (cyan for decisions, yellow for execution, green for completion)

---

## PHASE 3: DATA CONSISTENCY (Impact: 7/10)
**Goal:** Fix inconsistent data formatting and states  
**Duration:** 1.5 hours

### Task 3.1: Standardize Cost Display

**Implementation:**

1. **Create utility function: `src/utils/formatters.ts`**
```typescript
export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}

export function formatCostDetailed(cost: number): string {
  return `$${cost.toFixed(4)}`; // For detailed views
}

export function formatResponseTime(seconds: number): string {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`;
  }
  return `${seconds.toFixed(2)}s`;
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}
```

2. **Find all instances of cost display and replace:**

Search for patterns like:
- `$${cost}` → Replace with `formatCost(cost)`
- `$${totalCost.toFixed(4)}` → Replace with `formatCost(totalCost)`

Use this command to find them:
```bash
cd L:\nicedev-Project\MW-Vision\mw-vision-app
grep -r "\$\${.*}" src/ --include="*.tsx" --include="*.ts"
```

3. **Update header cost display:**

Find the header component showing "Cost: $4.5600 / $10" and change to:
```typescript
import { formatCost } from '../utils/formatters';

// In component:
<div>Cost: {formatCost(currentCost)} / {formatCost(budget)}</div>
```

**Validation:**
- All costs show 2 decimals: $2.47, not $2.4700
- Header shows: "Cost: $4.56 / $10"
- Team View agent costs show: $0.98, $1.97, etc.

---

### Task 3.2: Fix Agent States

**Implementation:**

1. **Update agent status logic in backend:**

Already handled in Task 1.1 - agents are 'idle' by default, 'running' during execution.

2. **Add status badge logic in frontend:**

```typescript
// In AgentCard or wherever agent status is displayed

function getStatusBadge(agent: Agent) {
  if (agent.status === 'running') {
    return (
      <span style={{
        background: '#39ff14',
        color: '#000',
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 'bold'
      }}>
        RUNNING
      </span>
    );
  } else if (agent.status === 'paused') {
    return (
      <span style={{
        background: '#ffbe0b',
        color: '#000',
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 'bold'
      }}>
        PAUSED
      </span>
    );
  } else {
    return (
      <span style={{
        background: '#8892a6',
        color: '#000',
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '11px',
        fontWeight: 'bold'
      }}>
        IDLE
      </span>
    );
  }
}
```

**Validation:**
- Agents show "IDLE" when Tasks Completed = 0 and status = 'idle'
- Agents show "RUNNING" when actively executing (Response Time > 0)
- Status changes in real-time via WebSocket

---

### Task 3.3: Fix Estimated Cost Calculation

**Implementation:**

1. **Update header stats component:**

Find where "Estimated Cost: $3.00" is displayed and change to dynamic calculation:

```typescript
import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { formatCost } from '../utils/formatters';

function HeaderStats() {
  const [stats, setStats] = useState({ totalCost: 0, totalTasks: 0 });
  const COST_BUDGET = 10.00;

  useEffect(() => {
    // Poll stats every 5 seconds
    const interval = setInterval(async () => {
      try {
        const data = await api.getStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    }, 5000);

    // Initial fetch
    api.getStats().then(setStats).catch(console.error);

    return () => clearInterval(interval);
  }, []);

  const remainingBudget = COST_BUDGET - stats.totalCost;

  return (
    <div>
      <div>Cost: {formatCost(stats.totalCost)} / {formatCost(COST_BUDGET)}</div>
      <div>Remaining: {formatCost(remainingBudget)}</div>
    </div>
  );
}
```

**Validation:**
- Estimated/Remaining cost updates in real-time
- Formula: Budget ($10) - Total Cost Accumulated
- As tasks execute, remaining budget decreases

---

## PHASE 4: OSINT-MW INTEGRATION (Impact: 6/10)
**Goal:** Add Venezuela intelligence pipeline as demo use case  
**Duration:** 2 hours

### Task 4.1: Create OSINT Workflow

**Implementation:**

1. **Add OSINT pipeline to backend:**

In `backend/src/server.ts`, add new agent:

```typescript
const agents: Map<string, Agent> = new Map([
  // ... existing agents ...
  ['osint-analyzer', {
    id: 'osint-analyzer',
    name: 'OSINT Analyzer',
    model: 'claude-3-haiku', // Fast for entity extraction
    status: 'idle',
    tasksCompleted: 0,
    totalCost: 0,
    lastResponseTime: 0,
    lastUpdate: new Date().toISOString()
  }]
]);
```

2. **Add OSINT workflow endpoint:**

```typescript
app.post('/api/workflows/osint-pipeline', async (req, res) => {
  const { documents } = req.body; // Array of Venezuela intelligence documents
  
  const pipeline = {
    id: `osint-${Date.now()}`,
    status: 'running',
    steps: [
      { name: 'Entity Extraction', agent: 'osint-analyzer', status: 'pending' },
      { name: 'Classification', agent: 'osint-analyzer', status: 'pending' },
      { name: 'Validation', agent: 'debugger', status: 'pending' }
    ],
    totalCost: 0
  };

  // Simulate pipeline execution
  // In real implementation, this would process documents
  broadcastToClients({ type: 'workflow_started', pipeline });

  setTimeout(() => {
    pipeline.steps[0].status = 'running';
    broadcastToClients({ type: 'workflow_update', pipeline });
  }, 500);

  setTimeout(() => {
    pipeline.steps[0].status = 'completed';
    pipeline.steps[1].status = 'running';
    broadcastToClients({ type: 'workflow_update', pipeline });
  }, 2000);

  setTimeout(() => {
    pipeline.steps[1].status = 'completed';
    pipeline.steps[2].status = 'running';
    broadcastToClients({ type: 'workflow_update', pipeline });
  }, 4000);

  setTimeout(() => {
    pipeline.steps[2].status = 'completed';
    pipeline.status = 'completed';
    pipeline.totalCost = 0.05; // Calculated based on actual API usage
    broadcastToClients({ type: 'workflow_completed', pipeline });
    res.json(pipeline);
  }, 6000);
});
```

3. **Add OSINT workflow trigger in Flow View:**

```typescript
// Add button in Flow View to trigger OSINT pipeline

<button
  onClick={async () => {
    try {
      await fetch('http://localhost:8080/api/workflows/osint-pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          documents: ['venezuela_intelligence_doc_1.pdf'] 
        })
      });
    } catch (error) {
      console.error('Failed to start OSINT pipeline:', error);
    }
  }}
  style={{
    position: 'absolute',
    bottom: '20px',
    left: '20px',
    background: '#ff006e',
    color: '#fff',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 'bold',
    cursor: 'pointer'
  }}
>
  🇻🇪 Run Venezuela OSINT Pipeline
</button>
```

4. **Show workflow progress in Flow View:**

```typescript
// Listen for workflow events
useWebSocket((data) => {
  if (data.type === 'workflow_started' || data.type === 'workflow_update') {
    // Update UI to show which step is running
    // Highlight the corresponding agent node
    // Show progress indicator
  }
});
```

**Validation:**
- Click "Run Venezuela OSINT Pipeline" button
- See pipeline execute through 3 steps
- Entity Extraction → Classification → Validation
- Agents highlight as they work
- Mission Log shows pipeline progress
- Total cost calculated and displayed

---

## PHASE 5: HYDRA PROTOCOL SIMPLIFICATION (Impact: 5/10)
**Goal:** Make Hydra Protocol optional, not mandatory  
**Duration:** 1 hour

### Task 5.1: Add Feature Flag

**Implementation:**

1. **Create config file: `src/config/features.ts`**
```typescript
export const features = {
  hydraProtocol: false, // Set to true to enable
  blueprintView: true,
  osintWorkflows: true,
  realTimeMonitoring: true
};
```

2. **Update Blueprint View:**

Find where Hydra Protocol is rendered:

```typescript
import { features } from '../config/features';

// In Blueprint View component:
{features.hydraProtocol && (
  <div className="hydra-protocol-section">
    {/* Hydra Protocol UI */}
  </div>
)}

{!features.hydraProtocol && (
  <div style={{
    padding: '20px',
    background: 'rgba(255, 190, 11, 0.1)',
    border: '1px solid #ffbe0b',
    borderRadius: '6px',
    color: '#ffbe0b'
  }}>
    ⚠️ Hydra Protocol is disabled. Enable in features.ts for advanced security.
  </div>
)}
```

**Validation:**
- With `hydraProtocol: false`, Hydra section shows warning
- With `hydraProtocol: true`, Hydra section appears
- App functions normally with feature disabled

---

## PHASE 6: UI POLISH (Impact: 4/10)
**Goal:** Fix minor visual inconsistencies  
**Duration:** 1 hour

### Task 6.1: Fix "Launch Crew" Button

**Implementation:**

1. **Rename button:**

Find the "Launch Crew" button and change to:

```typescript
<button
  onClick={handleStartWorkflow}
  style={{
    background: '#39ff14',
    color: '#000',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: 'bold',
    cursor: 'pointer'
  }}
>
  ▶ Start Workflow
</button>
```

2. **Implement actual functionality:**

```typescript
async function handleStartWorkflow() {
  // Get all idle agents
  const response = await fetch('http://localhost:8080/api/agents');
  const agents = await response.json();
  
  // Execute a test task on each agent
  for (const agent of agents) {
    if (agent.status === 'idle') {
      await api.executeTask(agent.id, `Test task for ${agent.name}`);
      // Wait 1 second between tasks to avoid overwhelming
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}
```

**Validation:**
- Button renamed to "Start Workflow"
- Clicking button executes test tasks on all idle agents
- Agents transition to RUNNING state
- Mission Log shows activity

---

### Task 6.2: Fix Canvas Empty Space

**Implementation:**

1. **Adjust node positions for better density:**

```typescript
// In Flow View, reposition nodes closer together

const nodes = [
  {
    id: 'strategic-coordinator',
    position: { x: 400, y: 150 }, // Move up slightly
    // ...
  },
  {
    id: 'debugger',
    position: { x: 150, y: 300 }, // Position around SC
    // ...
  },
  {
    id: 'code-reviewer',
    position: { x: 650, y: 300 },
    // ...
  },
  {
    id: 'test-generator',
    position: { x: 400, y: 450 },
    // ...
  },
  {
    id: 'osint-analyzer',
    position: { x: 150, y: 450 }, // Add OSINT node
    // ...
  }
];
```

2. **Fix mini-map inconsistency:**

The mini-map should reflect actual canvas. Ensure React Flow's `<MiniMap>` component is properly configured:

```typescript
<MiniMap
  nodeColor={(node) => {
    if (node.id === 'strategic-coordinator') return '#00d9ff';
    if (node.data.status === 'running') return '#39ff14';
    return '#8892a6';
  }}
  style={{
    background: 'rgba(10, 14, 26, 0.8)',
    border: '1px solid #00d9ff'
  }}
/>
```

**Validation:**
- Nodes are more densely arranged
- Mini-map colors match actual node states
- Canvas doesn't feel empty

---

## PHASE 7: TESTING & VALIDATION (Impact: 3/10)
**Goal:** Ensure everything works end-to-end  
**Duration:** 1 hour

### Task 7.1: End-to-End Test Script

**Implementation:**

Create `mw-vision-app/test-e2e.sh`:

```bash
#!/bin/bash

echo "🧪 MW-Vision End-to-End Test"
echo "=============================="
echo ""

# Test 1: Backend API
echo "1. Testing Backend API..."
response=$(curl -s http://localhost:8080/api/agents)
if [[ $response == *"debugger"* ]]; then
  echo "   ✅ Backend API responding"
else
  echo "   ❌ Backend API failed"
  exit 1
fi

# Test 2: WebSocket
echo "2. Testing WebSocket..."
# (WebSocket test would require a Node script, skip for now)
echo "   ⚠️  Manual test required: Check browser console for 'WebSocket connected'"

# Test 3: Execute Task
echo "3. Testing Task Execution..."
response=$(curl -s -X POST http://localhost:8080/api/agents/debugger/execute \
  -H "Content-Type: application/json" \
  -d '{"task":"Test task"}')
if [[ $response == *"success"* ]]; then
  echo "   ✅ Task execution working"
else
  echo "   ❌ Task execution failed"
  exit 1
fi

# Test 4: Stats
echo "4. Testing Stats..."
response=$(curl -s http://localhost:8080/api/stats)
if [[ $response == *"totalCost"* ]]; then
  echo "   ✅ Stats endpoint working"
else
  echo "   ❌ Stats endpoint failed"
  exit 1
fi

echo ""
echo "=============================="
echo "✅ All automated tests passed!"
echo ""
echo "Manual checks required:"
echo "  - Open http://localhost:5189"
echo "  - Navigate to Flow View - see Strategic Coordinator"
echo "  - Navigate to Team View - see real Response Times"
echo "  - Navigate to Mission Log - see activity logs"
echo "  - Click 'Start Workflow' - verify agents activate"
echo ""
```

**Validation:**
Run the script:
```bash
cd L:\nicedev-Project\MW-Vision\mw-vision-app
bash test-e2e.sh
```

All tests should pass.

---

## FINAL REPORTING FORMAT

After completing ALL phases, provide a report in this EXACT format:

```markdown
# MW-VISION CORRECTION REPORT
**Date:** [Current Date]
**Execution Time:** [Total hours]
**Status:** [COMPLETED / PARTIALLY COMPLETED / FAILED]

## PHASES COMPLETED

### Phase 1: Critical Fixes ✅ / ❌ / ⚠️
- [ ] Task 1.1: Mock Backend Server
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]
- [ ] Task 1.2: Frontend API Integration
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]
- [ ] Task 1.3: Strategic Coordinator Visualization
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]

### Phase 2: Mission Log ✅ / ❌ / ⚠️
- [ ] Task 2.1: Rename and Redesign Chat View
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]

### Phase 3: Data Consistency ✅ / ❌ / ⚠️
- [ ] Task 3.1: Standardize Cost Display
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]
- [ ] Task 3.2: Fix Agent States
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]
- [ ] Task 3.3: Fix Estimated Cost Calculation
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]

### Phase 4: OSINT-MW Integration ✅ / ❌ / ⚠️
- [ ] Task 4.1: Create OSINT Workflow
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]

### Phase 5: Hydra Protocol Simplification ✅ / ❌ / ⚠️
- [ ] Task 5.1: Add Feature Flag
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]

### Phase 6: UI Polish ✅ / ❌ / ⚠️
- [ ] Task 6.1: Fix "Launch Crew" Button
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]
- [ ] Task 6.2: Fix Canvas Empty Space
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Notes: [Any issues or observations]

### Phase 7: Testing & Validation ✅ / ❌ / ⚠️
- [ ] Task 7.1: End-to-End Test Script
  - Status: [COMPLETED / FAILED / SKIPPED]
  - Test Results: [Pass / Fail for each test]

## VALIDATION CHECKLIST

### Backend
- [ ] Backend starts without errors on port 8080
- [ ] `/api/agents` returns JSON array
- [ ] `/api/stats` returns valid stats
- [ ] WebSocket server accepts connections

### Frontend
- [ ] Frontend starts without errors on port 5189
- [ ] Strategic Coordinator visible in Flow View
- [ ] Mission Log shows real-time activity
- [ ] Team View displays real Response Times (not 0.0s)
- [ ] Costs formatted consistently (2 decimals)
- [ ] Agent states accurate (IDLE when not working)

### Integration
- [ ] Click "Start Workflow" → agents activate
- [ ] WebSocket updates UI in real-time
- [ ] Mission Log shows routing decisions
- [ ] Task execution increments Tasks Completed
- [ ] Costs accumulate correctly

## ISSUES ENCOUNTERED

[List any blockers, errors, or unexpected problems]

## FILES MODIFIED

[List all files changed, created, or deleted]

## SCREENSHOTS

[If possible, include screenshots of:]
1. Flow View with Strategic Coordinator
2. Team View showing real data
3. Mission Log with activity
4. Backend terminal showing logs

## NEXT STEPS RECOMMENDED

[Any additional work needed or improvements suggested]

---

**Report generated by:** Project A.C.E.
**Execution environment:** Windows, L:\nicedev-Project\MW-Vision
**Backend:** Express + WebSocket on port 8080
**Frontend:** Vite + React on port 5189
```

---

## CRITICAL REMINDERS FOR AI-CODER

1. **BACKUP BEFORE MODIFYING:**
   ```bash
   cp important-file.tsx important-file.tsx.backup
   ```

2. **COMMIT AFTER EACH PHASE:**
   ```bash
   git add -A
   git commit -m "Phase X: Description"
   ```

3. **VALIDATE AFTER EACH TASK:**
   - Run `npm run dev` in both backend and frontend
   - Open browser to `http://localhost:5189`
   - Verify the specific feature works

4. **IF STUCK:**
   - Check existing codebase for similar patterns
   - Search for error messages online
   - Provide me with the error and what you tried

5. **NO ASSUMPTIONS:**
   - If file path uncertain → use `find` command
   - If API endpoint missing → create it first
   - If syntax unclear → check existing code

---

## SUCCESS CRITERIA

At the end of ALL phases, the following MUST be true:

✅ Backend server running on port 8080  
✅ Frontend running on port 5189  
✅ Strategic Coordinator visible in Flow View  
✅ Real-time updates via WebSocket working  
✅ Mission Log shows routing decisions  
✅ Team View displays real Response Times (>0.0s)  
✅ Costs formatted consistently ($X.XX format)  
✅ Agent states accurate (RUNNING when executing)  
✅ "Start Workflow" button functional  
✅ OSINT workflow can be triggered  
✅ End-to-end test script passes  

---

**END OF PROMPT**

---

## HOW TO USE THIS PROMPT

1. **Give this entire document to Project A.C.E.**
2. **A.C.E. should work through phases sequentially**
3. **After completion, A.C.E. provides the formatted report**
4. **Victor reviews report and provides feedback**
5. **Iterate on any failed or problematic tasks**

---

*Document prepared by: Claude (Strategic Analysis)*  
*For execution by: Project A.C.E. (AI-Coder)*  
*Target: MW-Vision Restoration*  
*Priority: CRITICAL*
