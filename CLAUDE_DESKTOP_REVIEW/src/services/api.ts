const API_BASE = 'http://localhost:8000/api';

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
