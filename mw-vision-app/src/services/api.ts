const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api';

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
    /**
     * Los agentes, vengan como vengan.
     *
     * Los dos puntos de entrada hablan dialectos distintos y el frontend se
     * escribió contra el que NO arranca:
     *
     *   src/main.py       ->  [ { id, name, model, status, totalCost, ... } ]
     *   routers/agents.py ->  { agents: [ { id, name, model, status, cost,
     *                                        last_update } ], total_cost }
     *
     * PM2 arranca el segundo. Sin normalizar, `agents.find` reventaba y React
     * desmontaba el árbol entero: pantalla en blanco. No se veía porque el 404
     * de /api/stats mataba la inicialización antes de llegar aquí.
     */
    async getAgents(): Promise<Agent[]> {
        const response = await fetch(`${API_BASE}/agents`);
        if (!response.ok) throw new Error('Failed to fetch agents');
        const cuerpo = await response.json();
        const crudos: any[] = Array.isArray(cuerpo)
            ? cuerpo
            : Array.isArray(cuerpo?.agents) ? cuerpo.agents : [];
        if (!Array.isArray(cuerpo) && !Array.isArray(cuerpo?.agents)) {
            // Ni array ni {agents:[…]}: se devuelve vacío y se dice, en vez de
            // dejar que un `.find` sobre un objeto tumbe la aplicación.
            console.error(
                '[api] /agents devolvió una forma que no reconozco:',
                cuerpo);
        }
        return crudos.map((a) => ({
            id: String(a.id ?? ''),
            name: String(a.name ?? ''),
            model: String(a.model ?? ''),
            status: (a.status ?? 'idle') as Agent['status'],
            tasksCompleted: Number(a.tasksCompleted ?? a.tasks_completed ?? 0),
            totalCost: Number(a.totalCost ?? a.cost ?? a.total_cost ?? 0),
            lastResponseTime: Number(
                a.lastResponseTime ?? a.last_response_time ?? 0),
            lastUpdate: String(a.lastUpdate ?? a.last_update ?? ''),
        }));
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
