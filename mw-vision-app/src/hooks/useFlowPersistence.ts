/**
 * useFlowPersistence — React Flow layout persistence via localStorage.
 *
 * Saves and restores node positions and edge configurations so the
 * canvas layout survives page reloads. Falls back gracefully when
 * localStorage is unavailable.
 */

import { useCallback } from 'react'
import type { Node, Edge } from '@xyflow/react'

const STORAGE_KEY = 'mw-vision:flow-layout'

interface FlowLayout {
  nodes: Pick<Node, 'id' | 'position'>[]
  edges: Edge[]
  savedAt: string
}

/**
 * Merge saved positions back into freshly-computed nodes.
 * Positions are the only persistent field; data stays live from the store.
 */
export function applyPersistedPositions(nodes: Node[], saved: FlowLayout): Node[] {
  const posMap = new Map(saved.nodes.map(n => [n.id, n.position]))
  return nodes.map(node => {
    const pos = posMap.get(node.id)
    return pos ? { ...node, position: pos } : node
  })
}

export function useFlowPersistence() {
  /** Persist only id + position for each node plus the full edge list. */
  const saveLayout = useCallback((nodes: Node[], edges: Edge[]) => {
    try {
      const layout: FlowLayout = {
        nodes: nodes.map(({ id, position }) => ({ id, position })),
        edges,
        savedAt: new Date().toISOString(),
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(layout))
    } catch {
      // Silently ignore QuotaExceededError or private-browsing restrictions.
    }
  }, [])

  /** Load previously saved layout. Returns null when nothing is stored. */
  const loadLayout = useCallback((): FlowLayout | null => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return null
      return JSON.parse(raw) as FlowLayout
    } catch {
      return null
    }
  }, [])

  /** Remove persisted layout (e.g. when user clicks "Reset Layout"). */
  const clearLayout = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }, [])

  return { saveLayout, loadLayout, clearLayout }
}
