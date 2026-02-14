/**
 * MW-Vision App - Visual Command Center for AI Agents
 * 
 * Main application component with navigation and real-time status.
 */

import { useState, useEffect } from 'react'
import { Activity, Network, Users, MessageSquare, Box, Wifi, WifiOff, Zap } from 'lucide-react'
import FlowView from './views/FlowView'
import TeamView from './views/TeamView'
import ChatView from './views/ChatView'
import BlueprintView from './views/BlueprintView'
import { wsService } from './services/websocketService'
import { useCrewStore } from './stores/crewStore'

type ViewType = 'flow' | 'team' | 'chat' | 'blueprint'

function App() {
  const [activeView, setActiveView] = useState<ViewType>('flow')
  const [wsStatus, setWsStatus] = useState<string>('disconnected')
  const { connectionStatus, totalCost, budgetLimit, isCrewRunning } = useCrewStore()

  // Initialize WebSocket connection
  useEffect(() => {
    console.log('[App] Initializing MW-Vision Visual Command Center...')
    
    // Set up connection status listener using store subscription
    const unsubscribe = useCrewStore.subscribe((state) => {
      setWsStatus(state.connectionStatus)
    })
    
    // Try to connect to backend
    wsService.connect('ws://localhost:8000/ws')
    
    return () => {
      wsService.disconnect()
      unsubscribe()
    }
  }, [])

  // Get status display
  const getStatusDisplay = () => {
    if (totalCost > budgetLimit) {
      return { color: 'text-red-500', icon: Zap, text: 'BUDGET EXCEEDED' }
    }
    if (isCrewRunning) {
      return { color: 'text-green-500', icon: Activity, text: 'RUNNING' }
    }
    switch (connectionStatus) {
      case 'connected':
        return { color: 'text-green-500', icon: Wifi, text: 'CONNECTED' }
      case 'connecting':
        return { color: 'text-yellow-500', icon: Wifi, text: 'CONNECTING...' }
      case 'error':
        return { color: 'text-red-500', icon: WifiOff, text: 'ERROR' }
      case 'simulating':
        return { color: 'text-orange-500', icon: Zap, text: 'SIMULATION' }
      default:
        return { color: 'text-gray-500', icon: WifiOff, text: 'OFFLINE' }
    }
  }

  const statusDisplay = getStatusDisplay()
  const StatusIcon = statusDisplay.icon

  const tabs = [
    { id: 'flow' as ViewType, name: 'Flow View', icon: Network },
    { id: 'team' as ViewType, name: 'Team View', icon: Users },
    { id: 'chat' as ViewType, name: 'Chat View', icon: MessageSquare },
    { id: 'blueprint' as ViewType, name: 'Blueprint View', icon: Box },
  ]

  return (
    <div className="min-h-screen bg-osint-bg text-osint-text">
      {/* Header */}
      <header className="glass-panel border-b border-osint-cyan/30">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-osint-cyan animate-pulse" />
              <div>
                <h1 className="text-2xl font-orbitron font-bold bg-gradient-to-r from-osint-cyan to-osint-purple bg-clip-text text-transparent">
                  MW-VISION
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-osint-text-dim font-mono">
                    Visual Command Center for AI Agents
                  </span>
                  <span className="text-xs text-osint-cyan font-orbitron font-semibold px-2 py-0.5 bg-osint-cyan/10 rounded">
                    ONE STEP AHEAD
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-6">
              {/* Connection Status */}
              <div className="flex items-center gap-2 px-4 py-2 bg-osint-panel/50 rounded-lg border border-osint-cyan/20">
                <StatusIcon className={`w-4 h-4 ${statusDisplay.color} ${connectionStatus === 'connected' ? 'animate-pulse' : ''}`} />
                <span className={`text-sm font-medium ${statusDisplay.color}`}>
                  {statusDisplay.text}
                </span>
              </div>
              
              {/* Cost Display */}
              <div className="flex items-center gap-2 px-4 py-2 bg-osint-panel/50 rounded-lg border border-osint-cyan/20">
                <span className="text-sm text-osint-text-dim">Cost:</span>
                <span className={`text-sm font-mono font-semibold ${
                  totalCost > budgetLimit ? 'text-red-500' : 
                  totalCost > budgetLimit * 0.8 ? 'text-orange-500' : 'text-osint-green'
                }`}>
                  ${totalCost.toFixed(4)}
                </span>
                <span className="text-xs text-osint-text-muted">/ ${budgetLimit}</span>
              </div>
              
              {/* Budget Status */}
              <div className="w-24 h-2 bg-osint-panel rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${
                    totalCost > budgetLimit ? 'bg-red-500' :
                    totalCost > budgetLimit * 0.8 ? 'bg-orange-500' : 'bg-osint-green'
                  }`}
                  style={{ width: `${Math.min((totalCost / budgetLimit) * 100, 100)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="border-b border-osint-cyan/20">
        <div className="max-w-[1920px] mx-auto px-6">
          <div className="flex gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeView === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id)}
                  className={`
                    flex items-center gap-2 px-6 py-3 font-medium transition-all
                    ${isActive
                      ? 'bg-osint-cyan/10 text-osint-cyan border-b-2 border-osint-cyan'
                      : 'text-osint-text-dim hover:text-osint-text hover:bg-osint-panel/50'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-[1920px] mx-auto p-6">
        {activeView === 'flow' && <FlowView />}
        {activeView === 'team' && <TeamView />}
        {activeView === 'chat' && <ChatView />}
        {activeView === 'blueprint' && <BlueprintView />}
      </main>
    </div>
  )
}

export default App
