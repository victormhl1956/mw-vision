/**
 * MW-Vision Chat View
 * 
 * Natural Language Command Interface for controlling AI crews.
 * Integrated with WebSocket for real-time communication.
 */

import { useState, useEffect, useRef } from 'react'
import { Send, Terminal, Zap, Play, Pause, FileCode, AlertTriangle } from 'lucide-react'
import { useCrewStore } from '../stores/crewStore'
import { wsService } from '../services/websocketService'

interface Message {
  id: string
  type: 'user' | 'system' | 'agent' | 'error'
  content: string
  agent?: string
  timestamp?: string
}

export default function ChatView() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to MW-Vision Command Interface. Type a command or use quick actions below.',
      timestamp: new Date().toISOString()
    }
  ])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { isCrewRunning, totalCost, budgetLimit } = useCrewStore()

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Add system message helper
  const addSystemMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'system',
      content,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, newMessage])
  }

  // Add agent message helper
  const addAgentMessage = (agent: string, content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'agent',
      agent,
      content,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, newMessage])
  }

  // Process natural language commands
  const processCommand = (cmd: string): boolean => {
    const normalized = cmd.toLowerCase().trim()
    
    // Launch/Start commands
    if (normalized.match(/^(launch|start|run)\s+(.*)/)) {
      addSystemMessage('🚀 Launching crew...')
      useCrewStore.getState().launchCrew()
      return true
    }
    
    // Pause commands
    if (normalized.includes('pause') || normalized.includes('stop')) {
      addSystemMessage('⏸️ Pausing crew...')
      useCrewStore.getState().pauseCrew()
      return true
    }
    
    // Status commands
    if (normalized.includes('status')) {
      const status = isCrewRunning ? 'Running' : 'Paused'
      const cost = totalCost.toFixed(4)
      addSystemMessage(`📊 Crew Status: ${status} | Total Cost: $${cost} | Budget: $${budgetLimit}`)
      return true
    }
    
    // Cost commands
    if (normalized.includes('cost') || normalized.includes('budget') || normalized.includes('spend')) {
      addSystemMessage(`💰 Current Cost: $${totalCost.toFixed(4)} | Budget Limit: $${budgetLimit}`)
      if (totalCost > budgetLimit * 0.8) {
        addSystemMessage('⚠️ Warning: Approaching budget limit!')
      }
      return true
    }
    
    // Reset commands
    if (normalized.includes('reset')) {
      addSystemMessage('🔄 Resetting crew...')
      useCrewStore.getState().resetCrew()
      addSystemMessage('✅ Crew reset complete. All agents idle.')
      return true
    }
    
    // Help command
    if (normalized.includes('help') || normalized === '?') {
      addSystemMessage('📖 Available commands:')
      addSystemMessage('• "Launch crew" - Start all agents')
      addSystemMessage('• "Pause crew" - Stop all agents')
      addSystemMessage('• "Status" - Show crew status')
      addSystemMessage('• "Cost" or "Budget" - Show current spending')
      addSystemMessage('• "Reset" - Reset all agents')
      return true
    }
    
    return false
  }

  const handleSend = () => {
    if (!input.trim()) return
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    
    // Process command
    const processed = processCommand(input)
    
    if (!processed) {
      addSystemMessage(`⚠️ Unknown command: "${input}". Type "help" for available commands.`)
    }
    
    setInput('')
  }

  const handleQuickCommand = (command: string) => {
    setInput(command)
    handleSend()
  }

  const getStatusColor = () => {
    if (totalCost > budgetLimit) return 'text-red-500'
    if (totalCost > budgetLimit * 0.8) return 'text-orange-500'
    return 'text-green-500'
  }

  return (
    <div className="space-y-6">
      {/* Chat Container */}
      <div className="glass-panel rounded-lg flex flex-col h-[500px]">
        {/* Header */}
        <div className="p-4 border-b border-osint-cyan/20">
          <h2 className="text-xl font-orbitron font-bold text-osint-cyan flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            Natural Language Command Interface
          </h2>
          <div className="flex items-center gap-4 mt-2 text-sm">
            <span className="text-osint-text-dim">
              Status: <span className={getStatusColor()}>{isCrewRunning ? '🟢 Running' : '🔴 Paused'}</span>
            </span>
            <span className="text-osint-text-dim">
              Cost: <span className={getStatusColor()}>${totalCost.toFixed(4)}</span>
            </span>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[75%] rounded-lg p-3 ${
                msg.type === 'user' 
                  ? 'bg-osint-cyan/20 border border-osint-cyan/50' 
                  : msg.type === 'system'
                  ? 'bg-osint-purple/10 border border-osint-purple/30'
                  : msg.type === 'error'
                  ? 'bg-red-500/10 border border-red-500/30'
                  : 'bg-osint-panel border border-osint-text-dim/20'
              }`}>
                {msg.type === 'agent' && (
                  <div className="text-xs text-osint-cyan font-semibold mb-1 flex items-center gap-1">
                    <Zap className="w-3 h-3" />
                    {msg.agent}
                  </div>
                )}
                <div className={`text-sm ${
                  msg.type === 'user' ? 'text-osint-text' : 'text-osint-text-dim'
                }`}>
                  {msg.content}
                </div>
                {msg.timestamp && (
                  <div className="text-xs text-osint-text-muted mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-osint-cyan/20">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="Type a command... (e.g., 'Launch crew', 'Status', 'Cost')"
              className="flex-1 bg-osint-panel border border-osint-cyan/30 rounded-lg px-4 py-3 text-osint-text placeholder-osint-text-muted focus:outline-none focus:border-osint-cyan transition-colors"
            />
            <button
              onClick={handleSend}
              className="px-6 py-3 bg-osint-cyan/20 border border-osint-cyan text-osint-cyan rounded-lg hover:bg-osint-cyan/30 transition-all flex items-center gap-2 font-medium"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Quick Commands */}
      <div className="glass-panel p-5 rounded-lg">
        <h3 className="text-lg font-semibold text-osint-text mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-osint-cyan" />
          Quick Commands
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button 
            onClick={() => handleQuickCommand('Launch crew')}
            className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-cyan hover:shadow-[0_0_15px_rgba(0,212,255,0.2)] transition-all group"
          >
            <div className="text-osint-cyan font-semibold text-sm flex items-center gap-2">
              <Play className="w-4 h-4 group-hover:animate-pulse" />
              Launch Crew
            </div>
            <div className="text-osint-text-dim text-xs mt-1">Start all agents</div>
          </button>
          
          <button 
            onClick={() => handleQuickCommand('Pause crew')}
            className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-orange hover:shadow-[0_0_15px_rgba(255,153,0,0.2)] transition-all group"
          >
            <div className="text-osint-orange font-semibold text-sm flex items-center gap-2">
              <Pause className="w-4 h-4" />
              Pause Crew
            </div>
            <div className="text-osint-text-dim text-xs mt-1">Stop all agents</div>
          </button>
          
          <button 
            onClick={() => handleQuickCommand('Status')}
            className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-purple hover:shadow-[0_0_15px_rgba(157,78,221,0.2)] transition-all group"
          >
            <div className="text-osint-purple font-semibold text-sm flex items-center gap-2">
              <FileCode className="w-4 h-4" />
              Status
            </div>
            <div className="text-osint-text-dim text-xs mt-1">View crew status</div>
          </button>
          
          <button 
            onClick={() => handleQuickCommand('Cost')}
            className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-green hover:shadow-[0_0_15px_rgba(0,255,136,0.2)] transition-all group"
          >
            <div className="text-osint-green font-semibold text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Cost Check
            </div>
            <div className="text-osint-text-dim text-xs mt-1">View spending</div>
          </button>
        </div>
      </div>
    </div>
  )
}
