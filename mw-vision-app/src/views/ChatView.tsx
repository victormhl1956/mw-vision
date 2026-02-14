import { useState } from 'react'
import { Send, Terminal } from 'lucide-react'

const mockMessages = [
  { id: '1', type: 'user', content: 'Run bug_hunter crew on auth.py' },
  { id: '2', type: 'system', content: 'Launching bug_hunter crew with 3 agents...' },
  { id: '3', type: 'agent', agent: 'Debugger', content: 'Found 2 potential issues in authentication logic' },
  { id: '4', type: 'agent', agent: 'Code Reviewer', content: 'Reviewing suggested fixes...' },
]

export default function ChatView() {
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (input.trim()) {
      console.log('Sending:', input)
      setInput('')
    }
  }

  return (
    <div className="space-y-6">
      {/* Chat Container */}
      <div className="glass-panel rounded-lg flex flex-col h-[600px]">
        {/* Header */}
        <div className="p-4 border-b border-osint-cyan/20">
          <h2 className="text-xl font-orbitron font-bold text-osint-cyan flex items-center gap-2">
            <Terminal className="w-5 h-5" />
            Natural Language Command Interface
          </h2>
          <p className="text-sm text-osint-text-dim mt-1">
            Control your AI crews with natural language commands
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {mockMessages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[70%] rounded-lg p-4 ${
                msg.type === 'user' 
                  ? 'bg-osint-cyan/20 border border-osint-cyan' 
                  : msg.type === 'system'
                  ? 'bg-osint-purple/20 border border-osint-purple'
                  : 'bg-osint-panel border border-osint-text-dim/20'
              }`}>
                {msg.type === 'agent' && (
                  <div className="text-xs text-osint-cyan font-semibold mb-1">{msg.agent}</div>
                )}
                <div className={`${
                  msg.type === 'user' ? 'text-osint-text' : 'text-osint-text-dim'
                }`}>
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-osint-cyan/20">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type a command... (e.g., 'Launch debugging crew on main.py')"
              className="flex-1 bg-osint-panel border border-osint-cyan/30 rounded-lg px-4 py-3 text-osint-text placeholder-osint-text-muted focus:outline-none focus:border-osint-cyan"
            />
            <button
              onClick={handleSend}
              className="px-6 py-3 bg-osint-cyan/20 border border-osint-cyan text-osint-cyan rounded-lg hover:bg-osint-cyan/30 transition-all flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Quick Commands */}
      <div className="glass-panel p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-osint-text mb-4">Quick Commands</h3>
        <div className="grid grid-cols-2 gap-3">
          <button className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-cyan hover:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all">
            <div className="text-osint-cyan font-semibold text-sm flex items-center gap-2">
              🔍 Launch Bug Hunter
            </div>
            <div className="text-osint-text-dim text-xs mt-1">Start debugging crew</div>
          </button>
          <button className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-green hover:shadow-[0_0_15px_rgba(0,255,136,0.3)] transition-all">
            <div className="text-osint-green font-semibold text-sm flex items-center gap-2">
              🧪 Run Tests
            </div>
            <div className="text-osint-text-dim text-xs mt-1">Execute test generation crew</div>
          </button>
          <button className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-purple hover:shadow-[0_0_15px_rgba(157,78,221,0.3)] transition-all">
            <div className="text-osint-purple font-semibold text-sm flex items-center gap-2">
              📝 Code Review
            </div>
            <div className="text-osint-text-dim text-xs mt-1">Launch review crew</div>
          </button>
          <button className="text-left p-3 bg-osint-panel/50 border border-osint-cyan/20 rounded-lg hover:border-osint-orange hover:shadow-[0_0_15px_rgba(255,153,0,0.3)] transition-all">
            <div className="text-osint-orange font-semibold text-sm flex items-center gap-2">
              ⏸️ Pause All
            </div>
            <div className="text-osint-text-dim text-xs mt-1">Stop all running crews</div>
          </button>
        </div>
      </div>
    </div>
  )
}