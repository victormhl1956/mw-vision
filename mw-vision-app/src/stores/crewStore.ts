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

// ============================================================================
// Types
// ============================================================================

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

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error' | 'simulating'

interface CrewState {
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

// ============================================================================
// Initial Data
// ============================================================================

const initialAgents: Agent[] = [
  { 
    id: '1', 
    name: 'Debugger', 
    model: 'claude-3-5-sonnet', 
    status: 'idle', 
    cost: 0,
    lastUpdate: Date.now(),
    tasks: 0,
    averageResponseTime: 0
  },
  { 
    id: '2', 
    name: 'Code Reviewer', 
    model: 'deepseek-chat', 
    status: 'idle', 
    cost: 0,
    lastUpdate: Date.now(),
    tasks: 0,
    averageResponseTime: 0
  },
  { 
    id: '3', 
    name: 'Test Generator', 
    model: 'gpt-4o', 
    status: 'idle', 
    cost: 0,
    lastUpdate: Date.now(),
    tasks: 0,
    averageResponseTime: 0
  },
]

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
  
  // -------------------------------------------------------------------------
  // Core Crew Management
  // -------------------------------------------------------------------------
  
  launchCrew: () => {
    const { budgetLimit, checkBudgetLimit } = get()
    
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
        lastUpdate: Date.now()
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
        lastUpdate: Date.now()
      }))
    }))
  },
  
  resetCrew: () => {
    console.log('[CrewStore] 🔄 Resetting crew')
    set({ 
      isCrewRunning: false,
      totalCost: 0,
      estimatedCost: 0,
      agents: initialAgents.map(a => ({ ...a, lastUpdate: Date.now() }))
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
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, status, lastUpdate: Date.now() } : agent
      )
    }))
  },
  
  updateAgentCost: (id: string, cost: number) => {
    set((state) => {
      const updatedAgents = state.agents.map((agent) =>
        agent.id === id ? { ...agent, cost, lastUpdate: Date.now() } : agent
      )
      const newTotalCost = updatedAgents.reduce((sum, agent) => sum + agent.cost, 0)
      
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
