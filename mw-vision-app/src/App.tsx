import { useState, useEffect } from 'react'
import { Activity, Network, Users, MessageSquare, Box } from 'lucide-react'
import FlowView from './views/FlowView'
import TeamView from './views/TeamView'
import ChatView from './views/ChatView'
import BlueprintView from './views/BlueprintView'
import { wsService } from './services/websocketService'

type ViewType = 'flow' | 'team' | 'chat' | 'blueprint'

function App() {
  const [activeView, setActiveView] = useState<ViewType>('flow')

  // Initialize WebSocket connection
  useEffect(() => {
    console.log('[App] WebSocket service initialized')
    return () => {
      wsService.disconnect()
    }
  }, [])

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
                  <span className="text-xs text-osint-cyan font-orbitron font-semibold">
                    ONE STEP AHEAD
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm group cursor-help" title="Backend connected | WebSocket alive | 0 errors">
                <div className="w-2 h-2 rounded-full bg-osint-green animate-pulse" />
                <span className="text-osint-text-dim group-hover:text-osint-green transition-colors">System Active</span>
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
