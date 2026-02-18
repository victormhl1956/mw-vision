import { useEffect, useState, useCallback } from 'react'
import { Play, Pause, RotateCcw, DollarSign, Layers, LayoutGrid } from 'lucide-react'
import { useCrewStore } from '../stores/crewStore'
import { useToast } from '../components/Toast'
import FlowCanvas from '../components/FlowCanvas'
import { StrategicCoordinatorPanel } from '../components/StrategicCoordinatorPanel'
import { formatCost } from '../utils/formatters'

export default function FlowView() {
  const {
    agents,
    isCrewRunning,
    totalCost,
    estimatedCost,
    budgetLimit,
    launchCrew,
    pauseCrew,
    resetCrew,
    setEstimatedCost,
    updateAgentCost
  } = useCrewStore()

  const { showToast } = useToast()
  const [resetLayout, setResetLayout] = useState(false)

  const handleResetLayout = useCallback(() => {
    setResetLayout(true)
    showToast('info', 'Canvas layout reset to default positions.')
    // Flip flag back so future renders don't keep resetting
    setTimeout(() => setResetLayout(false), 100)
  }, [showToast])

  const handleLayoutSaved = useCallback(() => {
    showToast('success', 'Canvas layout saved to browser storage.')
  }, [showToast])

  // Calculate estimated cost based on current configuration
  useEffect(() => {
    // Simulate cost calculation: base cost per agent + model multiplier
    const modelCosts: Record<string, number> = {
      'Claude 3.5 Sonnet': 0.015,
      'DeepSeek Chat': 0.002,
      'GPT-4o': 0.03
    }

    const estimated = agents.reduce((sum, agent) => {
      const baseCost = modelCosts[agent.model] || 0.01
      // Estimate 1000 tokens per agent per run
      return sum + (baseCost * 100) // Rough estimate
    }, 0)

    setEstimatedCost(Number(estimated.toFixed(2)))
  }, [agents, setEstimatedCost])

  const budgetWarning = estimatedCost > budgetLimit

  const handleLaunch = () => {
    if (budgetWarning) {
      showToast('warning', `Estimated cost ($${estimatedCost}) exceeds budget limit ($${budgetLimit})`, 7000)
    }

    launchCrew()
    showToast('success', 'Crew launched successfully! All agents are now running.')

    // Simulate cost accumulation
    setTimeout(() => {
      agents.forEach((agent) => {
        const randomCost = Number((Math.random() * 2).toFixed(2))
        updateAgentCost(agent.id, randomCost)
      })
    }, 2000)
  }

  const handlePause = () => {
    pauseCrew()
    showToast('info', 'All running agents have been paused.')
  }

  const handleReset = () => {
    resetCrew()
    showToast('info', 'Crew has been reset. All costs cleared.')
  }

  return (
    <div className="space-y-6">
      {/* Controls & Cost Preview */}
      <div className="glass-panel p-6 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={handleLaunch}
              disabled={isCrewRunning}
              className="flex items-center gap-2 px-4 py-2 bg-osint-green/20 border border-osint-green text-osint-green rounded-lg hover:bg-osint-green/30 hover:shadow-[0_0_15px_rgba(0,255,136,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4" />
              Launch Crew
            </button>
            <button
              onClick={handlePause}
              disabled={!isCrewRunning}
              className="flex items-center gap-2 px-4 py-2 bg-osint-orange/20 border border-osint-orange text-osint-orange rounded-lg hover:bg-osint-orange/30 hover:shadow-[0_0_15px_rgba(255,153,0,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Pause className="w-4 h-4" />
              Pause All
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 px-4 py-2 bg-osint-cyan/20 border border-osint-cyan text-osint-cyan rounded-lg hover:bg-osint-cyan/30 hover:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              Reset
            </button>
          </div>

          {/* Cost Preview */}
          <div className={`flex items-center gap-3 px-6 py-3 rounded-lg border ${budgetWarning
            ? 'bg-osint-red/20 border-osint-red'
            : 'bg-osint-cyan/20 border-osint-cyan'
            }`}>
            <DollarSign className={`w-5 h-5 ${budgetWarning ? 'text-osint-red' : 'text-osint-cyan'}`} />
            <div>
              <div className="text-xs text-osint-text-dim">Estimated Cost</div>
              <div className={`text-lg font-bold font-mono ${budgetWarning ? 'text-osint-red' : 'text-osint-cyan'}`}>
                {formatCost(estimatedCost)}
              </div>
              {budgetWarning && (
                <div className="text-xs text-osint-red font-semibold mt-1">
                  Exceeds budget ({formatCost(budgetLimit)})
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Total Cost Display */}
        {totalCost > 0 && (
          <div className="mt-4 pt-4 border-t border-osint-cyan/20">
            <div className="flex items-center justify-between">
              <span className="text-osint-text-dim">Total Cost Accumulated:</span>
              <span className="text-xl font-bold font-mono text-osint-green">
                {formatCost(totalCost)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* React Flow Canvas */}
      <div className="relative glass-panel p-6 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-osint-cyan" />
            <h2 className="text-xl font-orbitron font-bold text-osint-cyan">
              Agent Flow Canvas
            </h2>
          </div>
          <button
            onClick={handleResetLayout}
            title="Reset canvas to default node positions"
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded bg-osint-purple/20 border border-osint-purple/50 text-osint-purple hover:bg-osint-purple/30 transition-colors"
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            Reset Layout
          </button>
        </div>
        <FlowCanvas resetLayout={resetLayout} onLayoutSaved={handleLayoutSaved} />
        <StrategicCoordinatorPanel />
        <div className="mt-4 p-4 bg-osint-panel/50 rounded border border-osint-cyan/20">
          <p className="text-osint-text-dim text-sm">
            <span className="text-osint-cyan font-semibold">Interactive Canvas:</span> Drag nodes to rearrange, connect agents to define workflows. Layout auto-saves on drag — click <span className="text-osint-cyan">Save Layout</span> to persist manually.
          </p>
        </div>
      </div>
    </div>
  )
}