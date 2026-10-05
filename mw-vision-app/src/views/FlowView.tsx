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
    setEstimatedCost
    // updateAgentCost ya no se usa aquí: el coste lo escribe el WebSocket
    // cuando hay trabajo real, no esta vista inventándolo al lanzar.
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

  // El coste ESTIMADO, que es legítimo calcular aquí mientras se diga de dónde
  // sale. Antes el comentario decía «Simulate cost calculation» y la pantalla
  // sólo ponía «Estimated Cost»: una cifra sin supuesto a la vista se lee como
  // una medida, y con ella se dispara el aviso de presupuesto.
  //
  // El supuesto es este, y ahora está escrito también en la interfaz: precios
  // por mil tokens de una tabla local, y 100 mil tokens por agente y corrida.
  // Los precios reales los sabe el API Manager; mientras esto no los lea, es
  // una estimación de servilleta y hay que decirlo.
  const PRECIOS_POR_MIL_TOKENS: Record<string, number> = {
    'Claude 3.5 Sonnet': 0.015,
    'DeepSeek Chat': 0.002,
    'GPT-4o': 0.03,
  }
  const PRECIO_DESCONOCIDO = 0.01
  const MILES_DE_TOKENS_POR_AGENTE = 100

  useEffect(() => {
    const estimado = agents.reduce((suma, agente) => {
      const precio = PRECIOS_POR_MIL_TOKENS[agente.model] ?? PRECIO_DESCONOCIDO
      return suma + precio * MILES_DE_TOKENS_POR_AGENTE
    }, 0)
    setEstimatedCost(Number(estimado.toFixed(2)))
  }, [agents, setEstimatedCost])

  const budgetWarning = estimatedCost > budgetLimit

  const handleLaunch = () => {
    if (budgetWarning) {
      showToast('warning', `Estimated cost ($${estimatedCost}) exceeds budget limit ($${budgetLimit})`, 7000)
    }

    launchCrew()
    showToast('success', 'Crew launched. Los costes reales llegarán por el WebSocket.')
    // Aquí había un `setTimeout` que dos segundos después repartía
    // `Math.random() * 2` como coste de cada agente. Era un SEGUNDO simulador,
    // independiente del backend, así que apagar MW_SIMULADOR no lo apagaba: el
    // número de gasto que se veía en pantalla lo inventaba el propio navegador.
    //
    // El coste llega por el WebSocket cuando hay trabajo real. Si no llega, se
    // queda en cero, que es la verdad: no haber medido no es haber gastado.
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
              <div className="text-xs text-osint-text-dim" title={
                `Estimación, no medida: ${MILES_DE_TOKENS_POR_AGENTE} mil ` +
                `tokens por agente a precios de una tabla local. El gasto real ` +
                `lo sabe el API Manager.`
              }>Coste estimado ·  supuesto</div>
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