/**
 * MW-Vision Crew Store - Zustand State Management
 * 
 * Enhanced with:
 * - Circuit breaker for budget limits
 * - Connection status management
 * - Realistic cost tracking with model pricing
 * 
 * This is the central state management for the entire application.
 */

import { create } from 'zustand'
import { hasWsToken, wsUrl } from '../services/wsUrl'
import { api, type Agent as ApiAgent } from '../services/api'

// ============================================================================
// Types
// ============================================================================

export interface Agent extends ApiAgent { }

export interface RoutingDecision {
  timestamp: string;
  query: string;
  complexity: number;
  selectedModel: string;
  reasoning: string;
  estimatedCost: number;
}

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error' | 'simulating'

interface CrewState {
  agents: Agent[]
  isCrewRunning: boolean
  totalCost: number
  estimatedCost: number
  budgetLimit: number
  connectionStatus: ConnectionStatus
  missionLogs: { timestamp: string, message: string, level: string }[]
  routingHistory: RoutingDecision[]

  // Actions - Initialization
  init: () => void

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

// ============================================================================
// Initial Data
// ============================================================================

const initialAgents: Agent[] = []

// ============================================================================
// Store Implementation
// ============================================================================

export const useCrewStore = create<CrewState>((set, get) => ({
  agents: initialAgents,
  isCrewRunning: false,
  totalCost: 0,
  estimatedCost: 0,
  budgetLimit: 10.0, // Default $10 budget
  connectionStatus: 'disconnected',
  missionLogs: [],
  routingHistory: [],

  // -------------------------------------------------------------------------
  // Initialization
  // -------------------------------------------------------------------------

  init: async () => {
    try {
      set({ connectionStatus: 'connecting' })

      // La siembra REST y el WebSocket son independientes, y aquí no lo eran:
      // `getStats()` iba primero, /api/stats da 404 en el entrypoint que
      // arranca PM2 —vive sólo en src/main.py— y la excepción saltaba al catch
      // de abajo, así que el WebSocket NO LLEGABA A CREARSE. La pantalla decía
      // «WebSocket: Connection Error» y la causa era un 404 de otra ruta.
      //
      // Y la segunda mitad del arreglo, que ayer dejé como deuda: la llamada a
      // /api/stats SOBRABA. Lo único que se leía de su respuesta era
      // `totalCost`, y ese número es `crew_state.total_cost`, que
      // routers/agents.py ya devuelve como `total_cost` en la MISMA petición
      // que trae los agentes — una ruta que el entrypoint de producción sí
      // sirve. Los otros cuatro campos de `Stats` no los leía nadie, y dos de
      // ellos (`savings`, `allSonnetCost`) se calculaban contra un
      // `avg_sonnet_cost = 0.01` escrito a mano: un ahorro inventado contra un
      // precio inventado. Registrar /api/stats en producción para callar un 404
      // habría sido meter dato falso donde no hacía falta ninguno.
      //
      // Cada fallo se cuenta por separado y ninguno impide al otro. Es el mismo
      // criterio que /health: degradado, y diciendo qué parte.
      try {
        const { agentes, costeTotal } = await api.getAgents()
        // `costeTotal` null = la respuesta no lo traía. No se escribe un cero
        // en su lugar: el saludo del WebSocket puede traerlo, y un cero
        // inventado se vería igual que un cero medido en la cabecera.
        set(costeTotal === null
          ? { agents: agentes }
          : { agents: agentes, totalCost: costeTotal })
      } catch (e) {
        console.error('[CrewStore] no pude leer los agentes:', e)
      }

      // El WebSocket, por `wsUrl()` y no a mano.
      //
      // Aquí se armaba la URL con `${VITE_WS_BASE}/ws` SIN TOKEN, y el backend
      // autentica /ws desde el 1-oct: cerraba cada conexión con 1008 y la
      // interfaz mostraba «Connection Error» sin causa. `services/wsUrl.ts`
      // existía y hacía lo correcto, pero sólo lo usaban useWebSocket.ts y
      // websocketService.ts, que no los importa NADIE. El arreglo estaba
      // escrito en el camino que no se ejecuta — el mismo defecto que vengo
      // persiguiendo, cometido al arreglarlo.
      const ws = new WebSocket(wsUrl('/ws'))

      ws.onmessage = (event: MessageEvent) => {
        try {
          const message = JSON.parse(event.data)
          const { type, agent, decision, actualCost, responseTime } = message

          switch (type) {
            // Los dos puntos de entrada hablan vocabularios distintos y el
            // frontend escuchaba el del que NO arranca: `src/main.py` manda
            // «initial_state» con los agentes en la raíz, y
            // `routers/websocket.py` —lo que sirve PM2— manda «init» con los
            // agentes dentro de `data`. El mensaje llegaba, no encajaba con
            // ningún caso, y el estado se quedaba en «Connecting…» para
            // siempre: socket abierto, autenticado y la pantalla diciendo que
            // no. Se aceptan los dos.
            case 'init':
            case 'initial_state': {
              const crudos: any[] = Array.isArray(message.agents)
                ? message.agents
                : Array.isArray(message.data?.agents) ? message.data.agents : []
              if (!crudos.length) {
                console.warn(
                  '[CrewStore] el saludo del WebSocket no traía agentes:',
                  message)
              }
              const agentes = crudos.map((a: any) => ({
                id: String(a.id ?? ''),
                name: String(a.name ?? ''),
                model: String(a.model ?? ''),
                status: (a.status ?? 'idle') as Agent['status'],
                tasksCompleted: Number(a.tasksCompleted ?? a.tasks_completed ?? 0),
                totalCost: Number(a.totalCost ?? a.cost ?? 0),
                lastResponseTime: Number(a.lastResponseTime ?? a.last_response_time ?? 0),
                lastUpdate: String(a.lastUpdate ?? a.last_update ?? ''),
              })) as Agent[]
              set({
                agents: agentes,
                totalCost: agentes.reduce((sum, a) => sum + (a.totalCost || 0), 0),
                connectionStatus: 'connected'
              })
              console.log(`[CrewStore] estado inicial por «${type}»: ${agentes.length} agentes`)
              break
            }

            case 'agent_status_changed':
              // Agent status changed (running/idle/paused)
              set((state) => ({
                agents: state.agents.map((a) =>
                  a.id === agent.id ? {
                    ...a,
                    status: agent.status,
                    lastUpdate: agent.lastUpdate
                  } : a
                )
              }))
              break

            case 'task_completed':
              // Task completed with actual cost and response time
              set((state) => {
                const updatedAgents = state.agents.map((a) =>
                  a.id === agent.id ? {
                    ...a,
                    tasksCompleted: agent.tasksCompleted,
                    totalCost: agent.totalCost,
                    lastResponseTime: agent.lastResponseTime,
                    status: agent.status,
                    lastUpdate: agent.lastUpdate
                  } : a
                )
                const newTotalCost = updatedAgents.reduce((sum, a) => sum + a.totalCost, 0)

                return {
                  agents: updatedAgents,
                  totalCost: newTotalCost
                }
              })
              console.log(`[CrewStore] Task completed: ${agent.name} - ${actualCost} in ${responseTime}s`)
              break

            case 'routing_decision':
              // Strategic Coordinator routing decision
              const logMessage = {
                timestamp: decision.timestamp,
                message: `SC: ${decision.reasoning}`,
                level: 'INFO'
              }
              set((state) => ({
                missionLogs: [logMessage, ...state.missionLogs].slice(0, 50),
                routingHistory: [decision, ...state.routingHistory].slice(0, 50)
              }))
              console.log('[CrewStore] Routing decision:', decision.selectedModel)
              break

            case 'pong':
              // Heartbeat response
              break

            default:
              console.log('[CrewStore] Unknown message type:', type)
          }
        } catch (e) {
          console.error('[CrewStore] WS Error:', e)
        }
      }

      ws.onclose = (evento: CloseEvent) => {
        // 1008 = el backend rechazó el token. Decirlo importa: sin esto, un
        // problema de configuración se lee como un problema de red, que es
        // exactamente lo que pasó durante un día entero.
        if (evento.code === 1008) {
          console.error(
            '[CrewStore] el backend rechazó la conexión (1008). ' +
            (hasWsToken
              ? 'El VITE_WS_TOKEN configurado no es válido para la clave de ' +
                'firma del backend.'
              : 'No hay VITE_WS_TOKEN: acúñalo con ' +
                'python backend/scripts/issue_ws_token.py'))
          set({ connectionStatus: 'error' })
          return
        }
        set({ connectionStatus: 'disconnected' })
      }
      ws.onerror = () => set({ connectionStatus: 'error' })

    } catch (error) {
      console.error('[CrewStore] Failed to initialize:', error)
      set({ connectionStatus: 'error' })
    }
  },

  // -------------------------------------------------------------------------
  // Core Crew Management
  // -------------------------------------------------------------------------

  launchCrew: () => {
    // ... existing launchCrew logic
    const { checkBudgetLimit } = get()

    // Check budget before launching
    if (checkBudgetLimit()) {
      console.warn('[CrewStore] ⚠️  Cannot launch crew: Budget limit exceeded')
      return
    }

    console.log('[CrewStore] 🚀 Launching crew')
    set({ isCrewRunning: true })

    // Update all agents to running
    set((state) => ({
      agents: state.agents.map((agent) => ({
        ...agent,
        status: 'running' as const,
        lastUpdate: new Date().toISOString()
      }))
    }))
  },

  pauseCrew: () => {
    console.log('[CrewStore] ⏸️  Pausing crew')
    set({ isCrewRunning: false })

    // Update all running agents to paused
    set((state) => ({
      agents: state.agents.map((agent) => ({
        ...agent,
        status: agent.status === 'running' ? 'paused' as const : agent.status,
        lastUpdate: new Date().toISOString()
      }))
    }))
  },

  resetCrew: () => {
    console.log('[CrewStore] 🔄 Resetting crew')
    set({
      isCrewRunning: false,
      totalCost: 0,
      estimatedCost: 0,
      agents: initialAgents.map(a => ({ ...a, lastUpdate: new Date().toISOString() }))
    })
  },

  // -------------------------------------------------------------------------
  // Agent Management
  // -------------------------------------------------------------------------

  addAgent: (agent: Agent) => {
    console.log(`[CrewStore] ➕ Adding agent: ${agent.name}`)
    set((state) => ({
      agents: [...state.agents, agent]
    }))
  },

  removeAgent: (id: string) => {
    console.log(`[CrewStore] ➖ Removing agent: ${id}`)
    set((state) => ({
      agents: state.agents.filter((agent) => agent.id !== id)
    }))
  },

  updateAgentStatus: (id: string, status: Agent['status']) => {
    set((state: CrewState) => ({
      agents: state.agents.map((agent: Agent) =>
        agent.id === id ? { ...agent, status, lastUpdate: new Date().toISOString() } : agent
      )
    }))
  },

  updateAgentCost: (id: string, totalCost: number) => {
    set((state: CrewState) => {
      const updatedAgents = state.agents.map((agent: Agent) =>
        agent.id === id ? { ...agent, totalCost, lastUpdate: new Date().toISOString() } : agent
      )
      const newTotalCost = updatedAgents.reduce((sum: number, agent: Agent) => sum + agent.totalCost, 0)

      // Auto-pause if budget exceeded (Circuit Breaker)
      const wouldExceed = newTotalCost > state.budgetLimit
      if (wouldExceed && state.isCrewRunning) {
        console.warn(`[CrewStore] 🛑 Circuit breaker triggered: Cost ($${newTotalCost.toFixed(2)}) exceeds budget ($${state.budgetLimit})`)
        // Return updated state but with crew paused
        const pausedAgents = updatedAgents.map((a) =>
          a.status === 'running' ? { ...a, status: 'paused' as const } : a
        )
        return {
          agents: pausedAgents,
          totalCost: newTotalCost,
          isCrewRunning: false
        }
      }

      return { agents: updatedAgents, totalCost: newTotalCost }
    })
  },

  // -------------------------------------------------------------------------
  // Cost & Budget
  // -------------------------------------------------------------------------

  setEstimatedCost: (cost: number) => {
    set({ estimatedCost: cost })
  },

  setBudgetLimit: (limit: number) => {
    console.log(`[CrewStore] 💰 Budget limit set to: $${limit}`)
    set({ budgetLimit: limit })
  },

  /**
   * Circuit Breaker: Check if estimated cost exceeds budget
   * Returns true if budget would be exceeded
   */
  checkBudgetLimit: () => {
    const { estimatedCost, budgetLimit } = get()
    const wouldExceed = estimatedCost > budgetLimit

    if (wouldExceed) {
      console.warn(`[CrewStore] ⚠️  Budget warning: Estimate ($${estimatedCost.toFixed(2)}) exceeds limit ($${budgetLimit})`)
    }

    return wouldExceed
  },

  // -------------------------------------------------------------------------
  // Connection Management
  // -------------------------------------------------------------------------

  setConnectionStatus: (status: ConnectionStatus) => {
    const statusLabels: Record<ConnectionStatus, string> = {
      'disconnected': 'Disconnected',
      'connecting': 'Connecting...',
      'connected': 'Connected',
      'error': 'Error',
      'simulating': 'Simulation Mode'
    }
    console.log(`[CrewStore] 📡 Connection status: ${statusLabels[status]}`)
    set({ connectionStatus: status })
  },

  setCrewRunning: (running: boolean) => {
    set({ isCrewRunning: running })
  },
}))

// ============================================================================
// Selectors (for optimized re-renders)
// ============================================================================

export const selectAgents = (state: CrewState) => state.agents
export const selectIsCrewRunning = (state: CrewState) => state.isCrewRunning
export const selectTotalCost = (state: CrewState) => state.totalCost
export const selectConnectionStatus = (state: CrewState) => state.connectionStatus
export const selectBudgetLimit = (state: CrewState) => state.budgetLimit
export const selectActiveAgents = (state: CrewState) =>
  state.agents.filter(a => a.status === 'running')
