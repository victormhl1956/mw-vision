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

/**
 * Lo que /api/agents devuelve, junto: los agentes y el coste acumulado.
 *
 * `costeTotal` es `null` cuando la respuesta no lo trae —la forma de
 * src/main.py es un array pelado y no lo lleva—. Null y 0 no son lo mismo:
 * null es «no vino», 0 es «vino y vale cero». Quien lo consume no debe
 * machacar un coste conocido con un cero inventado.
 */
export interface AgentesYCoste {
    agentes: Agent[];
    costeTotal: number | null;
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
    async getAgents(): Promise<AgentesYCoste> {
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
        const agentes = crudos.map((a) => ({
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
        const crudo = (cuerpo as any)?.total_cost ?? (cuerpo as any)?.totalCost;
        return {
            agentes,
            costeTotal: typeof crudo === 'number' && Number.isFinite(crudo)
                ? crudo
                : null,
        };
    },
};
