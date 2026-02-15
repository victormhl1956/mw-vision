/**
 * MW-Vision Team View
 * 
 * Agent Dashboard with real connection status.
 * Shows real-time agent metrics and system health.
 */

import { Zap, Target, DollarSign, Clock, X, ExternalLink } from 'lucide-react'
import { useCrewStore, type Agent } from '../stores/crewStore'
import { useState } from 'react'

// Modal Component for Agent Details
function AgentDetailModal({ agent, onClose }: { agent: Agent; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="glass-panel max-w-lg w-full rounded-lg p-6 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-osint-text-muted hover:text-osint-text">
          <X className="w-5 h-5" />
        </button>
        
        <div className="mb-6">
          <h3 className="text-xl font-bold text-osint-cyan">{agent.name}</h3>
          <div className="text-sm text-osint-text-dim font-mono mt-1">{agent.model}</div>
        </div>
        
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card p-3 rounded">
              <div className="text-xs text-osint-text-dim">Status</div>
              <div className={`font-semibold capitalize ${
                agent.status === 'running' ? 'text-osint-green' :
                agent.status === 'paused' ? 'text-osint-orange' :
                agent.status === 'error' ? 'text-osint-red' : 'text-osint-text-muted'
              }`}>{agent.status}</div>
            </div>
            <div className="glass-card p-3 rounded">
              <div className="text-xs text-osint-text-dim">Total Cost</div>
              <div className="font-semibold text-osint-cyan font-mono">${agent.cost.toFixed(4)}</div>
            </div>
          </div>
          
          <div className="glass-card p-3 rounded">
            <div className="text-xs text-osint-text-dim">Tasks Completed</div>
            <div className="text-2xl font-bold text-osint-text">{agent.tasks}</div>
          </div>
          
          <div className="glass-card p-3 rounded">
            <div className="text-xs text-osint-text-dim">Average Response Time</div>
            <div className="text-2xl font-bold text-osint-orange">{agent.averageResponseTime.toFixed(1)}s</div>
          </div>
          
          <div className="glass-card p-3 rounded">
            <div className="text-xs text-osint-text-dim">Last Activity</div>
            <div className="text-sm text-osint-text">{new Date(agent.lastUpdate).toLocaleString()}</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function TeamView() {
  const { agents, totalCost, isCrewRunning, connectionStatus, updateAgentStatus } = useCrewStore()
  const [selectedAgent, setSelectedAgent] = useState<typeof agents[number] | null>(null)
  
  const activeAgents = agents.filter(a => a.status === 'running').length
  const totalTasks = agents.reduce((sum, agent) => sum + agent.tasks, 0)
  const avgResponse = agents.reduce((sum, agent) => sum + agent.averageResponseTime, 0) / agents.length || 0

  // Real connection status based on WebSocket state
  const getConnectionColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'bg-osint-green'
      case 'connecting': return 'bg-osint-orange animate-pulse'
      case 'simulating': return 'bg-osint-purple'
      case 'error': return 'bg-osint-red'
      default: return 'bg-osint-text-muted'
    }
  }

  const getConnectionLabel = () => {
    switch (connectionStatus) {
      case 'connected': return 'Connected'
      case 'connecting': return 'Connecting...'
      case 'simulating': return 'Simulation Mode'
      case 'error': return 'Connection Error'
      default: return 'Disconnected'
    }
  }

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="glass-panel p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-osint-text-dim text-sm">Active Agents</div>
              <div className="text-3xl font-bold text-osint-cyan mt-1">{activeAgents}</div>
            </div>
            <Zap className="w-8 h-8 text-osint-cyan opacity-50" />
          </div>
          <div className="mt-3 pt-3 border-t border-osint-cyan/20">
            <div className="text-xs text-osint-text-dim">
              {activeAgents > 0 ? `${activeAgents} of ${agents.length} running` : 'All agents idle'}
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-osint-text-dim text-sm">Total Tasks</div>
              <div className="text-3xl font-bold text-osint-green mt-1">{totalTasks}</div>
            </div>
            <Target className="w-8 h-8 text-osint-green opacity-50" />
          </div>
          <div className="mt-3 pt-3 border-t border-osint-green/20">
            <div className="text-xs text-osint-text-dim">
              {totalTasks > 0 ? 'Tasks processed' : 'No tasks yet'}
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-osint-text-dim text-sm">Total Cost</div>
              <div className="text-3xl font-bold text-osint-purple mt-1 font-mono">
                ${totalCost.toFixed(2)}
              </div>
            </div>
            <DollarSign className="w-8 h-8 text-osint-purple opacity-50" />
          </div>
          <div className="mt-3 pt-3 border-t border-osint-purple/20">
            <div className="text-xs text-osint-text-dim">
              {totalCost > 0 ? 'Accumulated cost' : 'No cost yet'}
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-osint-text-dim text-sm">Avg Response</div>
              <div className="text-3xl font-bold text-osint-orange mt-1">
                {avgResponse.toFixed(1)}s
              </div>
            </div>
            <Clock className="w-8 h-8 text-osint-orange opacity-50" />
          </div>
          <div className="mt-3 pt-3 border-t border-osint-orange/20">
            <div className="text-xs text-osint-text-dim">
              Average agent response time
            </div>
          </div>
        </div>
      </div>

      {/* Agent Cards */}
      <div className="glass-panel p-6 rounded-lg">
        <h2 className="text-xl font-orbitron font-bold text-osint-cyan mb-6">
          Agent Status
        </h2>
        <div className="grid grid-cols-2 gap-6">
          {agents.map((agent) => (
            <div key={agent.id} className="glass-card p-6 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-osint-text">{agent.name}</h3>
                  <div className="text-sm text-osint-text-dim font-mono mt-1">{agent.model}</div>
                </div>
                <div className={`px-3 py-1 rounded-full text-xs font-semibold uppercase border ${
                  agent.status === 'running' 
                    ? 'bg-osint-green/20 border-osint-green text-osint-green' 
                    : agent.status === 'paused'
                    ? 'bg-osint-orange/20 border-osint-orange text-osint-orange'
                    : agent.status === 'error'
                    ? 'bg-osint-red/20 border-osint-red text-osint-red'
                    : 'bg-osint-panel border-osint-text-muted text-osint-text-muted'
                }`}>
                  {agent.status}
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-osint-text-dim text-sm">Tasks Completed</span>
                  <span className="text-osint-text font-semibold">{agent.tasks}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-osint-text-dim text-sm">Cost</span>
                  <span className="text-osint-cyan font-mono font-semibold">${agent.cost.toFixed(4)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-osint-text-dim text-sm">Response Time</span>
                  <span className="text-osint-text font-semibold">{agent.averageResponseTime.toFixed(1)}s</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-osint-text-dim text-sm">Last Update</span>
                  <span className="text-osint-text-muted text-xs">
                    {new Date(agent.lastUpdate).toLocaleTimeString()}
                  </span>
                </div>
              </div>

              <div className="flex gap-3 mt-4 pt-4 border-t border-osint-cyan/20">
                <button 
                  onClick={() => setSelectedAgent(agent)}
                  className="flex-1 px-3 py-2 text-sm bg-osint-cyan/20 border border-osint-cyan text-osint-cyan rounded hover:bg-osint-cyan/30 hover:shadow-[0_0_10px_rgba(0,212,255,0.3)] transition-all flex items-center justify-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Details
                </button>
                {agent.status === 'running' && (
                  <button 
                    onClick={() => updateAgentStatus(agent.id, 'paused')}
                    className="flex-1 px-3 py-2 text-sm bg-osint-orange/20 border border-osint-orange text-osint-orange rounded hover:bg-osint-orange/30 hover:shadow-[0_0_10px_rgba(255,153,0,0.3)] transition-all"
                  >
                    Pause
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Status - Now shows REAL connection status */}
      <div className="glass-panel p-6 rounded-lg">
        <h2 className="text-xl font-orbitron font-bold text-osint-cyan mb-4">
          System Status
        </h2>
        <div className="grid grid-cols-3 gap-6">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${isCrewRunning ? 'bg-osint-green animate-pulse' : 'bg-osint-text-muted'}`} />
            <div>
              <div className="text-sm text-osint-text-dim">Crew Status</div>
              <div className={`font-semibold ${isCrewRunning ? 'text-osint-green' : 'text-osint-text-muted'}`}>
                {isCrewRunning ? 'Running' : 'Idle'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${getConnectionColor()}`} />
            <div>
              <div className="text-sm text-osint-text-dim">WebSocket</div>
              <div className={`font-semibold ${
                connectionStatus === 'connected' ? 'text-osint-green' :
                connectionStatus === 'error' ? 'text-osint-red' :
                connectionStatus === 'simulating' ? 'text-osint-purple' :
                'text-osint-text-muted'
              }`}>
                {getConnectionLabel()}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${getConnectionColor()}`} />
            <div>
              <div className="text-sm text-osint-text-dim">Backend API</div>
              <div className={`font-semibold ${
                connectionStatus === 'connected' ? 'text-osint-green' :
                connectionStatus === 'error' ? 'text-osint-red' :
                connectionStatus === 'simulating' ? 'text-osint-purple' :
                'text-osint-text-muted'
              }`}>
                {connectionStatus === 'connected' || connectionStatus === 'simulating' ? 'Healthy' : 
                 connectionStatus === 'error' ? 'Error' : 'Offline'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Agent Detail Modal */}
      {selectedAgent && (
        <AgentDetailModal 
          agent={selectedAgent} 
          onClose={() => setSelectedAgent(null)} 
        />
      )}
    </div>
  )
}
