/**
 * La memoria del proyecto: conversaciones ingeridas, buscables.
 *
 * Por qué existe este fichero. El backend sirve `/api/chat/*` con consultas de
 * verdad —ingesta, listado, detalle y búsqueda sobre SQLite— y hasta hoy
 * NADIE lo llamaba: era una de las veinte rutas reales que ninguna pantalla
 * pedía. Capacidad construida y sin usar.
 *
 * Los tipos de aquí salen de lo que el backend devuelve de verdad, comprobado
 * contra la aplicación corriendo, no de lo que promete su firma. Dos cosas que
 * se comprobaron y que la interfaz tiene que respetar:
 *
 *   · `title` puede venir nulo (el analizador genérico de markdown no lo
 *     extrae), así que la lista necesita un recurso para nombrar una
 *     conversación sin título;
 *   · `intelligence` viene nulo cuando el backend no tiene OPENROUTER_API_KEY.
 *     Eso NO es «no hay nada que contar»: es «no se analizó», y la pantalla lo
 *     dice.
 */

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

export interface Plataforma {
  name: string
  display_name: string
  icon?: string
  export_instructions?: string
}

/** Metadatos de una conversación: lo que devuelven el listado y la búsqueda. */
export interface ConversacionResumen {
  conversation_id: string
  platform: string
  title: string | null
  source_url?: string | null
  message_count: number
  created_at?: string | null
  ingested_at: string
}

export interface Mensaje {
  role: string
  content: string
  timestamp?: string | null
}

export interface Hallazgo {
  level?: string
  kind?: string
  message?: string
  [k: string]: unknown
}

export interface Inteligencia {
  summary?: string | null
  main_topics?: string[]
  technologies?: string[]
  decisions?: string[]
  knowledge?: string[]
  osint_relevance?: string | null
  analyzed_at?: string
}

export interface Conversacion extends ConversacionResumen {
  messages: Mensaje[]
  warnings: string[]
  security_findings: Hallazgo[]
  /** Nulo o ausente = no se analizó. Nunca «no hay nada». */
  intelligence?: Inteligencia | null
}

export interface ResultadoIngesta {
  status: string
  conversation_id: string
  platform: string
  message_count: number
  security_findings: number
  warnings: string[]
  intelligence: Inteligencia | null
}

async function pedir<T>(camino: string, opciones?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${camino}`, opciones)
  if (!r.ok) {
    // El detalle del backend se propaga: un 422 de la ingesta dice POR QUÉ no
    // pudo extraer mensajes, y esconderlo detrás de «error» obliga al usuario a
    // adivinar.
    let detalle = ''
    try {
      const cuerpo = await r.json()
      detalle = typeof cuerpo?.detail === 'string' ? cuerpo.detail : ''
    } catch {
      detalle = ''
    }
    throw new Error(detalle || `el backend respondió ${r.status}`)
  }
  return (await r.json()) as T
}

export const memoria = {
  plataformas: () =>
    pedir<{ platforms: Plataforma[] } | Plataforma[]>('/chat/platforms'),

  listar: (limite = 50) =>
    pedir<{ conversations: ConversacionResumen[]; total: number }>(
      `/chat/conversations?limit=${encodeURIComponent(limite)}`),

  buscar: (q: string, limite = 20) =>
    pedir<{ query: string; results: ConversacionResumen[]; count: number }>(
      `/chat/search?q=${encodeURIComponent(q)}&limit=${encodeURIComponent(limite)}`),

  leer: (id: string) =>
    pedir<Conversacion>(`/chat/conversations/${encodeURIComponent(id)}`),

  ingerir: (contenido: string, plataforma?: string, analizar = true) =>
    pedir<ResultadoIngesta>('/chat/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: contenido,
        platform: plataforma || null,
        analyze: analizar,
      }),
    }),
}

/** Cómo llamar a una conversación cuyo título vino nulo. */
export function nombrar(c: ConversacionResumen): string {
  if (c.title && c.title.trim()) return c.title
  return `Sin título · ${c.platform} · ${c.message_count} mensajes`
}
