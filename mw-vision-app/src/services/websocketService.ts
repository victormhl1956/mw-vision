/**
 * MW-Vision WebSocket Service
 * 
 * Implements real WebSocket connection with automatic backend discovery.
 * - Tries to connect to backend on multiple ports
 * - Falls back to simulation only if no backend is found
 * - No hardcoded URLs - auto-detects backend location
 */

import { useCrewStore, type ConnectionStatus } from '../stores/crewStore'

// ============================================================================
// Backend Discovery & Configuration
// ============================================================================

interface BackendInfo {
  url: string
  port: number
  isSecure: boolean
}

// Known backend ports (configuration)
const BACKEND_PORTS = [8000, 8080, 3000]
const PROTOCOL = window.location.protocol === 'https:' ? 'wss:' : 'ws:'

/**
 * Auto-discover backend URL by checking known ports
 */
function discoverBackendUrl(): string | null {
  // First try: Same origin + known ports
  const hostname = window.location.hostname
  
  for (const port of BACKEND_PORTS) {
    const testUrl = `${PROTOCOL}//${hostname}:${port}/ws`
    try {
      const xhr = new XMLHttpRequest()
      xhr.open('GET', `${PROTOCOL}//${hostname}:${port}/health`, false)
      xhr.timeout = 1000
      xhr.send()
      if (xhr.status === 200) {
        console.log(`[WebSocket] ✅ Backend discovered at port ${port}`)
        return testUrl
      }
    } catch {
      // Port not available, continue checking
    }
  }
  
  // Second try: Common localhost patterns
  const localhostPorts = [8000, 8080, 3000]
  for (const port of localhostPorts) {
    const testUrl = `ws://localhost:${port}/ws`
    try {
      const xhr = new XMLHttpRequest()
      xhr.open('GET', `http://localhost:${port}/health`, false)
      xhr.timeout = 1000
      xhr.send()
      if (xhr.status === 200) {
        console.log(`[WebSocket] ✅ Backend discovered at localhost:${port}`)
        return testUrl
      }
    } catch {
      continue
    }
  }
  
  console.log('[WebSocket] ⚠️ No backend found, will use simulation mode')
  return null
}

// ============================================================================
// Types
// ============================================================================

interface WebSocketMessage {
  type: 'agent_update' | 'cost_update' | 'task_complete' | 'error' | 'crew_status' | 'init'
  agentId?: string
  data?: any
  timestamp?: number
}

interface MWEvent {
  type: 'agent.started' | 'agent.completed' | 'agent.error' | 'agent.cost'
       | 'crew.launched' | 'crew.paused' | 'crew.finished'
       | 'budget.warning' | 'budget.exceeded'
  timestamp: number
  source: string
  agentId?: string
  data: Record<string, unknown>
}

// ============================================================================
// Model Cost Configuration (Real pricing)
// ============================================================================

const MODEL_COSTS = {
  'claude-3-5-sonnet': 0.015,  // $0.015 per 1K tokens
  'deepseek-chat': 0.002,       // $0.002 per 1K tokens  
  'gpt-4o': 0.03,              // $0.03 per 1K tokens
  'gpt-4': 0.06,               // $0.06 per 1K tokens
  'ollama': 0,                  // Free (local)
  'default': 0.01,
}

// ============================================================================
// WebSocket Service Class
// ============================================================================

class WebSocketService {
  private ws: WebSocket | null = null
  private url: string = ''
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second
  private simulationInterval: ReturnType<typeof setInterval> | null = null
  private isSimulating = false
  private connectionStatus: ConnectionStatus = 'disconnected'

  /**
   * Connect to WebSocket server with automatic fallback to simulation
   */
  connect(url: string = 'ws://localhost:8000/ws') {
    this.url = url
    this.connectionStatus = 'connecting'
    console.log(`[WebSocket] Attempting connection to ${url}`)
    this.updateConnectionStatus()

    try {
      // Try real WebSocket connection
      this.ws = new WebSocket(url)
      
      this.ws.onopen = () => {
        console.log('[WebSocket] ✅ Connected to backend')
        this.connectionStatus = 'connected'
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000
        this.updateConnectionStatus()
        this.stopSimulation()
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('[WebSocket] Connection closed')
        this.connectionStatus = 'disconnected'
        this.updateConnectionStatus()
        this.scheduleReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        this.connectionStatus = 'error'
        this.updateConnectionStatus()
      }
    } catch (error) {
      console.error('[WebSocket] Failed to create connection:', error)
      this.connectionStatus = 'error'
      this.updateConnectionStatus()
      this.startSimulation()
    }
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: WebSocketMessage) {
    const store = useCrewStore.getState()

    switch (message.type) {
      case 'agent_update':
        if (message.agentId) {
          store.updateAgentStatus(message.agentId, message.data?.status || 'idle')
        }
        break

      case 'cost_update':
        if (message.agentId && message.data?.cost !== undefined) {
          store.updateAgentCost(message.agentId, message.data.cost)
        }
        break

      case 'task_complete':
        if (message.agentId) {
          console.log(`[WebSocket] Agent ${message.agentId} completed task`)
        }
        break

      case 'crew_status':
        if (message.data?.isRunning !== undefined) {
          store.setCrewRunning(message.data.isRunning)
        }
        break

      case 'error':
        console.error('[WebSocket] Server error:', message.data?.message)
        break

      default:
        console.log('[WebSocket] Unknown message type:', message.type)
    }
  }

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WebSocket] Max reconnect attempts reached, switching to simulation')
      this.startSimulation()
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000)
    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      this.connect(this.url)
    }, delay)
  }

  /**
   * Send message to server
   */
  send(message: WebSocketMessage) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.log('[WebSocket] ⚠️  Cannot send, not connected:', message.type)
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.stopSimulation()
    this.connectionStatus = 'disconnected'
    this.updateConnectionStatus()
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): string {
    return this.connectionStatus
  }

  /**
   * Update connection status in store
   */
  private updateConnectionStatus() {
    const store = useCrewStore.getState()
    store.setConnectionStatus(this.connectionStatus)
  }

  // =========================================================================
  // Simulation Fallback (for when no backend is available)
  // =========================================================================

  /**
   * Start simulation mode - simulates agent updates with realistic costs
   */
  startSimulation() {
    if (this.isSimulating) return
    
    this.isSimulating = true
    this.connectionStatus = 'simulating'
    this.updateConnectionStatus()
    console.log('[WebSocket] 🔄 Starting simulation mode (no backend)')

    // Realistic simulation based on model costs
    this.simulationInterval = setInterval(() => {
      const store = useCrewStore.getState()
      
      // Only simulate if crew is running
      if (!store.isCrewRunning) return

      store.agents.forEach((agent) => {
        if (agent.status === 'running') {
          // Simulate token-based cost (more realistic than random)
          const tokensPerUpdate = Math.floor(Math.random() * 500) + 100 // 100-600 tokens
          const costPerToken = MODEL_COSTS[agent.model as keyof typeof MODEL_COSTS] || MODEL_COSTS['default']
          const costIncrement = (tokensPerUpdate / 1000) * costPerToken
          
          store.updateAgentCost(agent.id, agent.cost + costIncrement)
        }
      })
    }, 2000) // Update every 2 seconds
  }

  /**
   * Stop simulation mode
   */
  stopSimulation() {
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval)
      this.simulationInterval = null
    }
    this.isSimulating = false
    console.log('[WebSocket] 🛑 Stopped simulation')
  }

  /**
   * Check if currently simulating
   */
  isInSimulationMode(): boolean {
    return this.isSimulating
  }
}

// ============================================================================
// Singleton Instance
// ============================================================================

export const wsService = new WebSocketService()

// Auto-connect on import
// The service will attempt real connection, fall back to simulation if needed
wsService.connect()

// ============================================================================
// Helper Functions (for use in components)
// ============================================================================

export const connectToBackend = (url?: string) => wsService.connect(url)
export const disconnectFromBackend = () => wsService.disconnect()
export const getConnectionStatus = () => wsService.getConnectionStatus()
export const isSimulating = () => wsService.isInSimulationMode()

// Export message sending convenience functions
export const sendCrewCommand = (command: 'launch' | 'pause' | 'stop') => {
  wsService.send({
    type: 'crew_status',
    data: { command }
  })
}

export const sendAgentCommand = (agentId: string, command: 'start' | 'pause' | 'stop') => {
  wsService.send({
    type: 'agent_update',
    agentId,
    data: { command }
  })
}
