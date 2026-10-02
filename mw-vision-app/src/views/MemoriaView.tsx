/**
 * Memoria: las conversaciones del proyecto, buscables.
 *
 * Por qué esta vista existe. El backend sirve `/api/chat/*` con consultas de
 * verdad sobre SQLite —ingesta, listado, detalle y búsqueda por contenido— y
 * hasta hoy ninguna pantalla lo pedía: era una de las veinte rutas reales que
 * nadie llamaba, mientras cinco paneles mostraban simulación y semilla.
 * Cablearla no construye nada nuevo; conecta lo que ya funcionaba.
 *
 * Las tres reglas que vienen de los defectos medidos hoy:
 *
 *   1. Vacío y error no se parecen. «No hay conversaciones» y «no pude
 *      preguntar» son estados distintos y se dicen distinto; un panel que
 *      enseña una lista vacía cuando la petición falló miente por omisión.
 *   2. Lo que no se midió se dice. Si el backend devuelve `intelligence: null`
 *      —porque le falta OPENROUTER_API_KEY— la ficha pone «sin análisis» y el
 *      motivo, en vez de dejar un hueco que se lee como «no hab a nada».
 *   3. Nada de dato inventado. Ni una lista escrita dentro, ni un contador
 *      estimado, ni un aviso de éxito antes de que el backend conteste.
 */

import { useCallback, useEffect, useState } from 'react'
import {
  AlertTriangle, Database, HelpCircle, Loader2, RefreshCw, Search, Upload,
} from 'lucide-react'
import {
  memoria, nombrar,
  type Conversacion, type ConversacionResumen,
} from '../services/memoria'

type Fuente = 'listado' | 'busqueda'

export default function MemoriaView() {
  const [filas, setFilas] = useState<ConversacionResumen[] | null>(null)
  const [fuente, setFuente] = useState<Fuente>('listado')
  const [consulta, setConsulta] = useState('')
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [abierta, setAbierta] = useState<Conversacion | null>(null)
  const [errorFicha, setErrorFicha] = useState<string | null>(null)

  const [pegado, setPegado] = useState('')
  const [ingiriendo, setIngiriendo] = useState(false)
  const [resultadoIngesta, setResultadoIngesta] = useState<string | null>(null)
  const [errorIngesta, setErrorIngesta] = useState<string | null>(null)

  const cargarListado = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const d = await memoria.listar()
      setFilas(d.conversations)
      setFuente('listado')
    } catch (e) {
      // filas = null, no [] : «no pude preguntar» no es «no hay nada».
      setFilas(null)
      setError(e instanceof Error ? e.message : 'no pude leer la memoria')
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => { void cargarListado() }, [cargarListado])

  const buscar = async (e: React.FormEvent) => {
    e.preventDefault()
    const q = consulta.trim()
    if (!q) { void cargarListado(); return }
    setCargando(true)
    setError(null)
    try {
      const d = await memoria.buscar(q)
      setFilas(d.results)
      setFuente('busqueda')
    } catch (err) {
      setFilas(null)
      setError(err instanceof Error ? err.message : 'la búsqueda falló')
    } finally {
      setCargando(false)
    }
  }

  const abrir = async (id: string) => {
    setErrorFicha(null)
    setAbierta(null)
    try {
      setAbierta(await memoria.leer(id))
    } catch (e) {
      setErrorFicha(e instanceof Error ? e.message : 'no pude abrir la ficha')
    }
  }

  const ingerir = async () => {
    const contenido = pegado.trim()
    if (!contenido) return
    setIngiriendo(true)
    setResultadoIngesta(null)
    setErrorIngesta(null)
    try {
      const r = await memoria.ingerir(contenido)
      // El aviso sale DESPUÉS de que el backend conteste, y cuenta lo que el
      // backend dijo: mensajes extraídos y hallazgos de seguridad reales.
      setResultadoIngesta(
        `Guardada: ${r.message_count} mensajes, plataforma ${r.platform}` +
        (r.security_findings
          ? `, ${r.security_findings} hallazgo(s) de seguridad`
          : '') +
        (r.intelligence ? '' : ' · sin análisis (el backend no tiene clave)'))
      setPegado('')
      await cargarListado()
    } catch (e) {
      setErrorIngesta(e instanceof Error ? e.message : 'la ingesta falló')
    } finally {
      setIngiriendo(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Ingesta */}
      <div className="glass-panel p-4 rounded-lg">
        <div className="flex items-center gap-2 mb-3">
          <Upload className="w-5 h-5 text-osint-cyan" />
          <h2 className="font-semibold">Guardar una conversación</h2>
        </div>
        <textarea
          value={pegado}
          onChange={(e) => setPegado(e.target.value)}
          placeholder="Pega aquí la exportación de ChatGPT, Claude, Gemini, DeepSeek o Perplexity. La plataforma se detecta sola."
          rows={4}
          className="w-full bg-osint-bg/60 border border-osint-cyan/20 rounded-lg p-3 text-sm font-mono text-osint-text placeholder:text-osint-text-muted focus:outline-none focus:border-osint-cyan/50"
        />
        <div className="flex items-center justify-between mt-3 gap-4">
          <div className="text-xs">
            {errorIngesta && (
              <span className="text-osint-red">{errorIngesta}</span>
            )}
            {resultadoIngesta && !errorIngesta && (
              <span className="text-osint-green">{resultadoIngesta}</span>
            )}
          </div>
          <button
            onClick={() => void ingerir()}
            disabled={ingiriendo || !pegado.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-osint-cyan/20 hover:bg-osint-cyan/30 text-osint-cyan rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          >
            {ingiriendo
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <Upload className="w-4 h-4" />}
            {ingiriendo ? 'Guardando…' : 'Guardar'}
          </button>
        </div>
      </div>

      {/* Búsqueda */}
      <form onSubmit={buscar} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-osint-text-dim absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            value={consulta}
            onChange={(e) => setConsulta(e.target.value)}
            placeholder="Buscar en el contenido de las conversaciones"
            className="w-full bg-osint-bg/60 border border-osint-cyan/20 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:border-osint-cyan/50"
          />
        </div>
        <button type="submit" disabled={cargando}
          className="px-4 py-2 bg-osint-cyan/20 hover:bg-osint-cyan/30 text-osint-cyan rounded-lg text-sm disabled:opacity-50">
          Buscar
        </button>
        <button type="button" onClick={() => { setConsulta(''); void cargarListado() }}
          disabled={cargando}
          className="flex items-center gap-2 px-4 py-2 border border-osint-cyan/20 text-osint-text-dim hover:text-osint-text rounded-lg text-sm disabled:opacity-50">
          <RefreshCw className={`w-4 h-4 ${cargando ? 'animate-spin' : ''}`} />
          Todas
        </button>
      </form>

      {/* Error de lectura: nunca una lista vacía disfrazada */}
      {error && (
        <div className="glass-panel p-4 rounded-lg border border-osint-red/40 bg-osint-red/5">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-osint-red mt-0.5 shrink-0" />
            <div className="text-sm">
              <div className="font-semibold text-osint-red">No pude leer la memoria</div>
              <div className="text-osint-text-dim mt-1">{error}</div>
              <div className="text-osint-text-muted text-xs mt-2">
                Esto no significa que no haya conversaciones guardadas: significa
                que no pude preguntar.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Listado */}
      {filas !== null && (
        <div className="glass-panel rounded-lg overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-osint-cyan/20">
            <Database className="w-4 h-4 text-osint-cyan" />
            <span className="font-semibold text-sm">
              {fuente === 'busqueda'
                ? `${filas.length} resultado(s) para «${consulta}»`
                : `${filas.length} conversación(es) guardada(s)`}
            </span>
          </div>
          {filas.length === 0 ? (
            <div className="px-4 py-6 text-sm text-osint-text-dim">
              {fuente === 'busqueda'
                ? 'La búsqueda no encontró nada con ese texto.'
                : 'La memoria está vacía todavía. Pega una exportación arriba para empezar.'}
            </div>
          ) : (
            <div className="divide-y divide-osint-cyan/10">
              {filas.map((c) => (
                <button key={c.conversation_id}
                  onClick={() => void abrir(c.conversation_id)}
                  className="w-full text-left px-4 py-3 hover:bg-osint-cyan/5 transition-colors flex items-center justify-between gap-4">
                  <span className="text-sm">{nombrar(c)}</span>
                  <span className="text-xs text-osint-text-muted font-mono shrink-0">
                    {c.platform} · {c.message_count} msg · {c.ingested_at.slice(0, 16).replace('T', ' ')}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {errorFicha && (
        <div className="glass-panel p-4 rounded-lg border border-osint-red/40 text-sm">
          <span className="text-osint-red">{errorFicha}</span>
        </div>
      )}

      {/* Ficha */}
      {abierta && (
        <div className="glass-panel rounded-lg overflow-hidden">
          <div className="flex items-start justify-between gap-4 px-4 py-3 border-b border-osint-cyan/20">
            <div>
              <div className="font-semibold text-sm">{nombrar(abierta)}</div>
              <div className="text-xs text-osint-text-muted font-mono mt-1">
                {abierta.platform} · {abierta.messages.length} mensajes ·
                guardada {abierta.ingested_at.slice(0, 16).replace('T', ' ')}
              </div>
            </div>
            <button onClick={() => setAbierta(null)}
              className="text-osint-text-dim hover:text-osint-text text-sm">✕</button>
          </div>

          {abierta.security_findings.length > 0 && (
            <div className="px-4 py-3 border-b border-osint-cyan/10 bg-osint-red/5">
              <div className="flex items-center gap-2 text-sm font-semibold text-osint-red">
                <AlertTriangle className="w-4 h-4" />
                {abierta.security_findings.length} hallazgo(s) de seguridad en esta conversación
              </div>
              <ul className="mt-2 space-y-1 text-xs text-osint-text-dim">
                {abierta.security_findings.map((h, i) => (
                  <li key={i}>
                    {[h.level, h.kind, h.message].filter(Boolean).join(' · ')}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="px-4 py-3 border-b border-osint-cyan/10">
            {abierta.intelligence ? (
              <div className="space-y-2 text-sm">
                {abierta.intelligence.summary && (
                  <p className="text-osint-text">{abierta.intelligence.summary}</p>
                )}
                {!!abierta.intelligence.decisions?.length && (
                  <div>
                    <div className="text-xs text-osint-text-dim mb-1">Decisiones</div>
                    <ul className="list-disc pl-5 text-xs space-y-1">
                      {abierta.intelligence.decisions.map((d, i) => <li key={i}>{d}</li>)}
                    </ul>
                  </div>
                )}
                {!!abierta.intelligence.main_topics?.length && (
                  <div className="text-xs text-osint-text-dim">
                    Temas: {abierta.intelligence.main_topics.join(', ')}
                  </div>
                )}
              </div>
            ) : (
              /* Un hueco se lee como «no había nada»; esto dice por qué no hay. */
              <div className="flex items-start gap-2 text-sm text-osint-text-dim">
                <HelpCircle className="w-4 h-4 text-osint-text-muted mt-0.5 shrink-0" />
                <span>
                  Sin análisis. El backend devuelve el resumen y las decisiones
                  sólo si tiene <code className="text-osint-text">OPENROUTER_API_KEY</code>;
                  la conversación está guardada y buscable igual.
                </span>
              </div>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto divide-y divide-osint-cyan/10">
            {abierta.messages.map((m, i) => (
              <div key={i} className="px-4 py-3">
                <div className="text-xs font-mono text-osint-cyan mb-1">{m.role}</div>
                <div className="text-sm whitespace-pre-wrap text-osint-text">{m.content}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
