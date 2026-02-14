import { create } from 'zustand'

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

interface CrewState {
  agents: Agent[]
  isCrewRunning: boolean
  totalCost: number
  estimatedCost: number
  budgetLimit: number
  
  // Actions
  launchCrew: () => void
  pauseCrew: () => void
  resetCrew: () => void
  updateAgentStatus: (id: string, status: Agent['status']) => void
  updateAgentCost: (id: string, cost: number) => void
  setEstimatedCost: (cost: number) => void
  setBudgetLimit: (limit: number) => void
}

const initialAgents: Agent[] = [
  { 
    id: '1', 
    name: 'Debugger', 
    model: 'Claude 3.5 Sonnet', 
    status: 'idle', 
    cost: 0,
    lastUpdate: Date.now(),
    tasks: 0,
    averageResponseTime: 0
  },
  { 
    id: '2', 
    name: 'Code Reviewer', 
    model: 'DeepSeek Chat', 
    status: 'idle', 
    cost: 0,
    lastUpdate: Date.now(),
    tasks: 0,
    averageResponseTime: 0
  },
  { 
    id: '3', 
    name: 'Test Generator', 
    model: 'GPT-4o', 
    status: 'idle', 
    cost: 0,
    lastUpdate: Date.now(),
    tasks: 0,
    averageResponseTime: 0
  },
]

export const useCrewStore = create<CrewState>((set, get) => ({
  agents: initialAgents,
  isCrewRunning: false,
  totalCost: 0,
  estimatedCost: 0,
  budgetLimit: 10.0, // Default $10 budget
  
  launchCrew: () => {
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
    set({ 
      isCrewRunning: false,
      totalCost: 0,
      estimatedCost: 0,
      agents: initialAgents.map(a => ({ ...a, lastUpdate: Date.now() }))
    })
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
      return { agents: updatedAgents, totalCost: newTotalCost }
    })
  },
  
  setEstimatedCost: (cost: number) => {
    set({ estimatedCost: cost })
  },
  
  setBudgetLimit: (limit: number) => {
    set({ budgetLimit: limit })
  },
}))
