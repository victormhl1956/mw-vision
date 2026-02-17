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

// Agent Node Data Type
interface AgentNodeData {
  label: string
  model: string
  status: 'idle' | 'running' | 'paused' | 'error'
  cost: number
}

// Custom Node Component
function AgentNode({ data }: { data: AgentNodeData }) {
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

// Custom Coordinator Node Component
function CoordinatorNode({ data }: { data: any }) {
  return (
    <div
      className="glass-card px-6 py-4 rounded-lg border-2 min-w-[250px] shadow-[0_0_30px_rgba(0,217,255,0.4)]"
      style={{
        borderColor: '#00d9ff',
        background: 'linear-gradient(135deg, rgba(0, 217, 255, 0.1), rgba(255, 0, 110, 0.1))'
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="w-3 h-3 rounded-full bg-osint-cyan animate-pulse" />
        <div className="font-bold text-lg text-osint-cyan font-orbitron">{data.label}</div>
      </div>
      <div className="text-xs text-osint-text-dim space-y-1">
        <div className="font-mono text-osint-purple">{data.subtitle}</div>
        <div className="mt-2 text-osint-text">{data.role}</div>
      </div>
    </div>
  )
}

const nodeTypes = {
  agent: AgentNode,
  coordinator: CoordinatorNode,
}

export default function FlowCanvas() {
  const { agents } = useCrewStore()

  // Convert agents to React Flow nodes
  const initialNodes: Node[] = useMemo(() => {
    const scAgent = agents.find(a => a.id === '0')
    const otherAgents = agents.filter(a => a.id !== '0')

    const agentNodes: Node[] = otherAgents.map((agent, index) => ({
      id: agent.id,
      type: 'agent',
      position: {
        x: index === 0 ? 100 : index === 1 ? 400 : 700,
        y: 450
      },
      data: {
        label: agent.name,
        model: agent.model,
        status: agent.status,
        cost: agent.totalCost.toFixed(2),
      },
    }))

    const scNode: Node = {
      id: 'strategic-coordinator',
      type: 'coordinator',
      position: { x: 350, y: 100 },
      data: {
        label: scAgent?.name || 'Strategic Coordinator',
        subtitle: scAgent?.model || 'Claude 3.5 Sonnet',
        role: scAgent?.status === 'running' ? 'ORCHESTRATING_MISSION...' : 'MISSION_CONTROL_IDLE',
        status: scAgent?.status || 'idle'
      }
    }

    return [scNode, ...agentNodes]
  }, [agents])

  const initialEdges: Edge[] = useMemo(() => {
    const otherAgents = agents.filter(a => a.id !== '0')
    return otherAgents.map(agent => ({
      id: `sc-to-${agent.id}`,
      source: 'strategic-coordinator',
      target: agent.id,
      animated: agent.status === 'running',
      label: agent.id === '1' ? 'Complexity Check' : 'Complexity Response',
      style: { stroke: agent.status === 'running' ? '#00ff88' : '#00d4ff', strokeWidth: 2 },
      labelStyle: { fill: '#8892a6', fontSize: 10, fontWeight: 'bold' }
    }))
  }, [agents])

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
        if (node.id === 'strategic-coordinator') return node
        const agent = agents.find((a) => a.id === node.id)
        if (agent) {
          return {
            ...node,
            data: {
              ...node.data,
              status: agent.status,
              cost: agent.totalCost.toFixed(2),
            },
          }
        }
        return node
      })
    )

    // Update edges animation
    setEdges((eds) =>
      eds.map(edge => {
        const agent = agents.find(a => edge.target === a.id)
        return {
          ...edge,
          animated: agent?.status === 'running'
        }
      })
    )
  }, [agents, setNodes, setEdges])

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
