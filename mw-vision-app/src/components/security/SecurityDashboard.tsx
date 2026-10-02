/**
 * MW-Vision Security Dashboard
 *
 * Lee /api/security. No afirma nada que no venga de ahí.
 *
 * Qué había antes, y por qué esto es distinto. Este panel era un `useState` con
 * ocho comprobaciones escritas a mano, todas en 'pass' —incluida
 * «Authentication: JWT token validation active»— una puntuación fija de 92, y un
 * botón «refrescar» que sumaba amenazas detectadas con Math.random(). Siguió
 * diciendo que la autenticación pasaba durante los ocho meses en que el endpoint
 * de WebSocket no autenticaba. Un panel de seguridad que no puede ponerse rojo
 * convierte la falta de medición en apariencia de seguridad.
 *
 * Tres reglas, por eso:
 *   1. cada comprobación viene del backend con su evidencia, y hay un tercer
 *      estado —«sin medir»— para lo que no se puede saber desde dentro del
 *      proceso (el TLS lo termina un proxy, la validación vive en cada
 *      manejador). Sin medir NO es verde.
 *   2. no hay puntuación. Una cifra única invita a promediar lo medido con lo no
 *      medido, y así «no lo sé» se vuelve «va bien».
 *   3. si la petición falla, el panel lo dice. Nunca cae a un verde por defecto.
 */

import { useCallback, useEffect, useState } from 'react'
import {
  Activity, AlertTriangle, CheckCircle, Eye, HelpCircle, Lock, RefreshCw,
  Server, Shield, XCircle,
} from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000/api'

type EstadoComprobacion = 'pasa' | 'falla' | 'no_se'

interface Comprobacion {
  name: string
  status: EstadoComprobacion
  evidence: string
}

interface Evidencia {
  status: 'secure' | 'partial' | 'critical' | 'unknown'
  checks: Comprobacion[]
  counts: { pasa: number; falla: number; no_se: number }
  score: null
  score_explanation: string
}

interface RespuestaSeguridad {
  evidence: Evidencia
  security_metrics?: {
    requests_blocked?: number
    threats_detected?: number
    invalid_messages?: number
    start_time?: string
  }
  active_connections?: number
}

interface SecurityDashboardProps {
  isOpen: boolean
  onClose: () => void
}

const ETIQUETA_ESTADO: Record<Evidencia['status'], string> = {
  secure: '🟢 TODO LO MEDIDO, EN ORDEN',
  partial: '🟡 EN ORDEN LO MEDIDO, Y QUEDA LO NO MEDIDO',
  critical: '🔴 HAY AL MENOS UN FALLO',
  unknown: '⚪ NO SE PUDO MEDIR NADA',
}

export default function SecurityDashboard({ isOpen, onClose }: SecurityDashboardProps) {
  const [datos, setDatos] = useState<RespuestaSeguridad | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [cargando, setCargando] = useState(false)

  const cargar = useCallback(async () => {
    setCargando(true)
    setError(null)
    try {
      const r = await fetch(`${API_BASE}/security`)
      if (!r.ok) throw new Error(`el backend respondió ${r.status}`)
      const cuerpo = (await r.json()) as RespuestaSeguridad
      if (!cuerpo?.evidence?.checks) {
        throw new Error('la respuesta no trae evidencia de seguridad')
      }
      setDatos(cuerpo)
    } catch (e) {
      // Un panel de seguridad que se pone verde cuando no puede medir es peor
      // que uno que no existe: aquí se queda sin datos y lo dice.
      setDatos(null)
      setError(e instanceof Error ? e.message : 'no pude leer /api/security')
    } finally {
      setCargando(false)
    }
  }, [])

  useEffect(() => {
    if (isOpen) void cargar()
  }, [isOpen, cargar])

  const icono = (estado: EstadoComprobacion) => {
    switch (estado) {
      case 'pasa': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'falla': return <XCircle className="w-4 h-4 text-red-500" />
      default: return <HelpCircle className="w-4 h-4 text-osint-text-muted" />
    }
  }

  if (!isOpen) return null

  const ev = datos?.evidence
  const met = datos?.security_metrics

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-osint-panel border border-osint-cyan/30 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">

        {/* Cabecera */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-osint-cyan/20 bg-gradient-to-r from-osint-panel to-osint-bg">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-osint-cyan" />
            <div>
              <h2 className="text-xl font-bold text-osint-text">Seguridad</h2>
              <p className="text-sm text-osint-text-dim">
                Lo que la aplicación puede demostrar de sí misma
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-osint-text-dim hover:text-osint-text transition-colors">✕</button>
        </div>

        {/* Error: nunca se cae a un verde por defecto */}
        {error && (
          <div className="px-6 py-4 border-b border-red-500/30 bg-red-500/10">
            <div className="flex items-start gap-3">
              <XCircle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" />
              <div>
                <div className="font-semibold text-red-400">No pude leer el estado de seguridad</div>
                <div className="text-sm text-osint-text-dim mt-1">{error}</div>
                <div className="text-xs text-osint-text-muted mt-2">
                  Esto no significa que todo esté bien ni que esté mal: significa
                  que no se sabe. El panel no muestra nada hasta que pueda medirlo.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recuento, en vez de una puntuación */}
        {ev && (
          <div className="px-6 py-4 border-b border-osint-cyan/20">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-5 h-5 text-osint-cyan" />
              <span className="font-semibold">{ETIQUETA_ESTADO[ev.status]}</span>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
                <div className="text-3xl font-bold text-green-500">{ev.counts.pasa}</div>
                <div className="text-xs text-osint-text-dim mt-1">comprobadas y en orden</div>
              </div>
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                <div className="text-3xl font-bold text-red-500">{ev.counts.falla}</div>
                <div className="text-xs text-osint-text-dim mt-1">fallan</div>
              </div>
              <div className="bg-osint-bg/50 border border-osint-cyan/10 rounded-lg p-4">
                <div className="text-3xl font-bold text-osint-text-muted">{ev.counts.no_se}</div>
                <div className="text-xs text-osint-text-dim mt-1">sin medir</div>
              </div>
            </div>
            <div className="text-xs text-osint-text-muted mt-3">{ev.score_explanation}</div>
          </div>
        )}

        {/* Contadores reales del proceso */}
        {met && (
          <div className="px-6 py-4 grid grid-cols-3 gap-4 border-b border-osint-cyan/20">
            <div className="flex items-center gap-2 text-sm">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
              <span>Peticiones bloqueadas: <b>{met.requests_blocked ?? '—'}</b></span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />
              <span>Amenazas detectadas: <b>{met.threats_detected ?? '—'}</b></span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Server className="w-4 h-4 text-osint-text-dim" />
              <span>Conexiones activas: <b>{datos?.active_connections ?? '—'}</b></span>
            </div>
          </div>
        )}

        {/* Las comprobaciones, cada una con su evidencia */}
        {ev && (
          <div className="px-6 py-4">
            <h3 className="font-semibold mb-3 flex items-center gap-2">
              <Eye className="w-4 h-4 text-osint-cyan" />
              Comprobaciones
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {ev.checks.map((c) => (
                <div
                  key={c.name}
                  className="flex items-start justify-between gap-4 px-4 py-2 bg-osint-bg/50 rounded-lg border border-osint-cyan/10"
                >
                  <div className="flex items-center gap-3 shrink-0">
                    {icono(c.status)}
                    <span className="text-sm font-medium">{c.name}</span>
                  </div>
                  {/* La evidencia va siempre visible, no en un tooltip: es lo
                      que permite discutir la comprobación en vez de creerla. */}
                  <span className="text-xs text-osint-text-dim text-right">{c.evidence}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pie */}
        <div className="px-6 py-4 border-t border-osint-cyan/20 bg-osint-bg/30 flex items-center justify-between">
          <span className="flex items-center gap-2 text-xs text-osint-text-muted">
            <Lock className="w-4 h-4" />
            {/* Aquí decía «All data encrypted at rest» y «SOC 2 Compliant».
                Las dos eran texto fijo; la segunda es además una afirmación con
                peso legal que nada en este código sostiene. */}
            Cada línea de arriba viene de /api/security con su evidencia. Lo que
            no se puede medir desde dentro del proceso aparece como «sin medir».
          </span>
          <button
            onClick={() => void cargar()}
            disabled={cargando}
            className="flex items-center gap-2 px-4 py-2 bg-osint-cyan/20 hover:bg-osint-cyan/30 text-osint-cyan rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${cargando ? 'animate-spin' : ''}`} />
            Volver a medir
          </button>
        </div>
      </div>
    </div>
  )
}
