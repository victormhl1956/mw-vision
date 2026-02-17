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
