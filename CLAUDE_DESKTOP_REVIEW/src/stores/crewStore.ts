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
      const agents = await api.getAgents()
      const stats = await api.getStats()

      set({
        agents,
        totalCost: stats.totalCost,
        connectionStatus: 'connected'
      })

      // Setup WebSocket - Pointing to real backend port
      const WS_URL = 'ws://localhost:8000/ws'
      const ws = new WebSocket(WS_URL)

      ws.onmessage = (event: MessageEvent) => {
        try {
          const message = JSON.parse(event.data)
          const { type, agent, decision, actualCost, responseTime } = message

          switch (type) {
            case 'initial_state':
              // Initial state from backend
              set({
                agents: message.agents,
                totalCost: message.agents.reduce((sum: number, a: Agent) => sum + (a.totalCost || 0), 0),
                connectionStatus: 'connected'
              })
              console.log('[CrewStore] Initial state loaded from backend')
              break

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

      ws.onclose = () => set({ connectionStatus: 'disconnected' })
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
