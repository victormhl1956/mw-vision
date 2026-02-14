import { useCallback, useMemo, useEffect } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useCrewStore } from '../stores/crewStore'

// Custom Node Component
function AgentNode({ data }: { data: any }) {
  const statusColor = 
    data.status === 'running' ? '#00ff88' :
    data.status === 'paused' ? '#ff9900' :
    data.status === 'error' ? '#ff3366' :
    '#6b7280'

  return (
    <div 
      className="glass-card px-4 py-3 rounded-lg border-2 min-w-[200px]"
      style={{ borderColor: statusColor }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div 
          className="w-2 h-2 rounded-full"
          style={{ backgroundColor: statusColor }}
        />
        <div className="font-semibold text-sm text-osint-text">{data.label}</div>
      </div>
      <div className="text-xs text-osint-text-dim space-y-1">
        <div className="font-mono">{data.model}</div>
        <div className="flex justify-between">
          <span>Cost:</span>
          <span className="text-osint-cyan font-mono">${data.cost}</span>
        </div>
      </div>
    </div>
  )
}

const nodeTypes = {
  agent: AgentNode,
}

export default function FlowCanvas() {
  const { agents } = useCrewStore()

  // Convert agents to React Flow nodes
  const initialNodes: Node[] = useMemo(() => 
    agents.map((agent, index) => ({
      id: agent.id,
      type: 'agent',
      position: { 
        x: 100 + (index % 2) * 300, 
        y: 100 + Math.floor(index / 2) * 150 
      },
      data: {
        label: agent.name,
        model: agent.model,
        status: agent.status,
        cost: agent.cost.toFixed(2),
      },
    })),
    [agents]
  )

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#00d4ff' } },
    { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: '#00d4ff' } },
  ]

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  // Update nodes when agents change
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        const agent = agents.find((a) => a.id === node.id)
        if (agent) {
          return {
            ...node,
            data: {
              ...node.data,
              status: agent.status,
              cost: agent.cost.toFixed(2),
            },
          }
        }
        return node
      })
    )
  }, [agents, setNodes])

  return (
    <div className="h-[500px] w-full rounded-lg overflow-hidden border border-osint-cyan/30">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        className="bg-osint-panel"
      >
        <Background color="#00d4ff" gap={16} size={1} />
        <Controls className="bg-osint-panel border border-osint-cyan/30 rounded" />
        <MiniMap 
          className="bg-osint-panel border border-osint-cyan/30 rounded"
          nodeColor={(node) => {
            const status = node.data.status
            return status === 'running' ? '#00ff88' :
                   status === 'paused' ? '#ff9900' :
                   status === 'error' ? '#ff3366' : '#6b7280'
          }}
        />
      </ReactFlow>
    </div>
  )
}
