/**
 * MW-Vision App - Visual Command Center for AI Agents
 * Enhanced with Security Dashboard & Browser Interactor
 */

import { useState, useEffect } from 'react'
import { Activity, Network, Users, MessageSquare, Box, Wifi, WifiOff, Zap, Shield, Play, Terminal } from 'lucide-react'
import FlowView from './views/FlowView'
import TeamView from './views/TeamView'
import ChatView from './views/ChatView'
import BlueprintView from './views/BlueprintView'
import SecurityDashboard from './components/security/SecurityDashboard'
import { wsService } from './services/websocketService'
import { useCrewStore } from './stores/crewStore'
import { runTests, getTestSummary } from './services/browserInteractor'

type ViewType = 'flow' | 'team' | 'chat' | 'blueprint'

function App() {
  const [activeView, setActiveView] = useState<ViewType>('flow')
  const [showSecurityDashboard, setShowSecurityDashboard] = useState(false)
  const [testRunning, setTestRunning] = useState(false)
  const [testResults, setTestResults] = useState<{ summary: any } | null>(null)
  const { connectionStatus, totalCost, budgetLimit, isCrewRunning } = useCrewStore()

  useEffect(() => {
    console.log('[App] Initializing MW-Vision...')
    const unsubscribe = useCrewStore.subscribe((state) => {
      console.log('[App] Connection status:', state.connectionStatus)
    })
    const hostname = window.location.hostname
    const wsUrl = `ws://${hostname}:8000/ws`
    console.log('[App] Connecting to:', wsUrl)
    wsService.connect(wsUrl)
    return () => {
      wsService.disconnect()
      unsubscribe()
    }
  }, [])

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

  const runBrowserTests = async () => {
    setTestRunning(true)
    console.log('[App] Starting browser tests...')
    try {
      await runTests()
      const summary = getTestSummary()
      setTestResults({ summary })
      console.log('[App] Tests complete:', summary)
    } catch (error) {
      console.error('[App] Test error:', error)
    } finally {
      setTestRunning(false)
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
      <SecurityDashboard isOpen={showSecurityDashboard} onClose={() => setShowSecurityDashboard(false)} />

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
                  <span className="text-sm text-osint-text-dim font-mono">Visual Command Center for AI Agents</span>
                  <span className="text-xs text-osint-cyan font-orbitron font-semibold px-2 py-0.5 bg-osint-cyan/10 rounded">ONE STEP AHEAD</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button onClick={() => setShowSecurityDashboard(true)} className="flex items-center gap-2 px-4 py-2 bg-osint-cyan/10 hover:bg-osint-cyan/20 text-osint-cyan rounded-lg border border-osint-cyan/30 transition-colors">
                <Shield className="w-4 h-4" />
                <span className="text-sm font-medium">Security</span>
              </button>

              <button onClick={runBrowserTests} disabled={testRunning} className="flex items-center gap-2 px-4 py-2 bg-osint-purple/10 hover:bg-osint-purple/20 text-osint-purple rounded-lg border border-osint-purple/30 transition-colors disabled:opacity-50">
                <Terminal className={`w-4 h-4 ${testRunning ? 'animate-spin' : ''}`} />
                <span className="text-sm font-medium">{testRunning ? 'Testing...' : 'Alpha Test'}</span>
              </button>

              <div className="flex items-center gap-2 px-4 py-2 bg-osint-panel/50 rounded-lg border border-osint-cyan/20">
                <StatusIcon className={`w-4 h-4 ${connectionStatus === 'connected' ? 'animate-pulse' : ''} ${statusDisplay.color}`} />
                <span className={`text-sm font-medium ${statusDisplay.color}`}>{statusDisplay.text}</span>
              </div>

              <div className="flex items-center gap-2 px-4 py-2 bg-osint-panel/50 rounded-lg border border-osint-cyan/20">
                <span className="text-sm text-osint-text-dim">Cost:</span>
                <span className={`text-sm font-mono font-semibold ${totalCost > budgetLimit ? 'text-red-500' : totalCost > budgetLimit * 0.8 ? 'text-orange-500' : 'text-osint-green'}`}>
                  ${totalCost.toFixed(4)}
                </span>
                <span className="text-xs text-osint-text-muted">/ ${budgetLimit}</span>
              </div>

              <div className="w-24 h-2 bg-osint-panel rounded-full overflow-hidden">
                <div className={`h-full transition-all duration-300 ${totalCost > budgetLimit ? 'bg-red-500' : totalCost > budgetLimit * 0.8 ? 'bg-orange-500' : 'bg-osint-green'}`} style={{ width: `${Math.min((totalCost / budgetLimit) * 100, 100)}%` }} />
              </div>
            </div>
          </div>
        </div>
      </header>

      {testResults && (
        <div className="bg-osint-purple/10 border-b border-osint-purple/30 px-6 py-3">
          <div className="flex items-center justify-between max-w-[1920px] mx-auto">
            <div className="flex items-center gap-4">
              <Play className="w-4 h-4 text-osint-purple" />
              <span className="text-sm text-osint-text">
                Alpha Test Results: 
                <span className="text-green-500 ml-2">✓ {testResults.summary.passed}/{testResults.summary.total} passed</span>
                <span className="text-osint-text-dim ml-2">({(testResults.summary.duration / 1000).toFixed(2)}s)</span>
              </span>
            </div>
            <button onClick={() => setTestResults(null)} className="text-xs text-osint-text-dim hover:text-osint-text">Dismiss</button>
          </div>
        </div>
      )}

      <div className="border-b border-osint-cyan/20">
        <div className="max-w-[1920px] mx-auto px-6">
          <div className="flex gap-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeView === tab.id
              return (
                <button key={tab.id} onClick={() => setActiveView(tab.id)} className={`flex items-center gap-2 px-6 py-3 font-medium transition-all ${isActive ? 'bg-osint-cyan/10 text-osint-cyan border-b-2 border-osint-cyan' : 'text-osint-text-dim hover:text-osint-text hover:bg-osint-panel/50'}`}>
                  <Icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </div>
        </div>
      </div>

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
