import { useCrewStore } from '../stores/crewStore'

interface WebSocketMessage {
  type: 'agent_update' | 'cost_update' | 'task_complete' | 'error'
  agentId?: string
  data?: any
}

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectInterval: NodeJS.Timeout | null = null
  private simulationInterval: NodeJS.Timeout | null = null
  private isSimulating = false

  connect(url: string = 'ws://localhost:8000/ws') {
    try {
      // In a real implementation, this would connect to a WebSocket server
      // For MVP, we'll simulate WebSocket behavior
      console.log('[WebSocket] Simulating connection to', url)
      this.startSimulation()
    } catch (error) {
      console.error('[WebSocket] Connection failed:', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval)
      this.reconnectInterval = null
    }
    this.stopSimulation()
  }

  startSimulation() {
    if (this.isSimulating) return
    
    this.isSimulating = true
    console.log('[WebSocket] Starting agent update simulation')

    // Simulate agent updates every 3 seconds
    this.simulationInterval = setInterval(() => {
      const store = useCrewStore.getState()
      
      // Only simulate if crew is running
      if (!store.isCrewRunning) return

      // Simulate random agent updates
      store.agents.forEach((agent) => {
        if (agent.status === 'running') {
          // Random chance to update this agent
          if (Math.random() > 0.5) {
            // Simulate cost increment
            const costIncrement = Number((Math.random() * 0.05).toFixed(3))
            store.updateAgentCost(agent.id, agent.cost + costIncrement)

            // Simulate task completion (random chance)
            if (Math.random() > 0.7) {
              console.log(`[WebSocket] Agent ${agent.name} completed a task`)
            }
          }
        }
      })
    }, 3000)
  }

  stopSimulation() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval)
      this.simulationInterval = null
    }
    this.isSimulating = false
    console.log('[WebSocket] Stopped agent update simulation')
  }

  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.log('[WebSocket] Simulating message send:', message)
    }
  }
}

// Singleton instance
export const wsService = new WebSocketService()

// Auto-connect on import
wsService.connect()
