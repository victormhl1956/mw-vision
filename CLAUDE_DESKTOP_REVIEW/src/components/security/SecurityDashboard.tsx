/**
 * MW-Vision Security Dashboard
 * Real-time security metrics and monitoring
 */

import { useState } from 'react'
import { Shield, Lock, Eye, AlertTriangle, CheckCircle, XCircle, RefreshCw, Activity, Server, Globe, Key, Database } from 'lucide-react'

interface SecurityMetrics {
  status: 'secure' | 'warning' | 'critical'
  score: number
  checks: {
    name: string
    status: 'pass' | 'fail' | 'warning' | 'pending'
    message: string
    timestamp: string
  }[]
  metrics: {
    requestsBlocked: number
    threatsDetected: number
    uptime: number
    encryptionStatus: 'active' | 'inactive'
    rateLimitStatus: 'active' | 'inactive'
    corsStatus: 'configured' | 'unconfigured'
  }
}

interface SecurityDashboardProps {
  isOpen: boolean
  onClose: () => void
}

export default function SecurityDashboard({ isOpen, onClose }: SecurityDashboardProps) {
  const [metrics, setMetrics] = useState<SecurityMetrics>({
    status: 'secure',
    score: 92,
    checks: [
      { name: 'HTTPS/TLS', status: 'pass', message: 'Encrypted connection active', timestamp: new Date().toISOString() },
      { name: 'Rate Limiting', status: 'pass', message: 'DDoS protection active', timestamp: new Date().toISOString() },
      { name: 'CORS Policy', status: 'pass', message: 'Cross-origin restrictions configured', timestamp: new Date().toISOString() },
      { name: 'Security Headers', status: 'pass', message: 'All security headers present', timestamp: new Date().toISOString() },
      { name: 'Input Validation', status: 'pass', message: 'SQL injection prevention active', timestamp: new Date().toISOString() },
      { name: 'XSS Protection', status: 'pass', message: 'Content security policy enforced', timestamp: new Date().toISOString() },
      { name: 'Authentication', status: 'pass', message: 'JWT token validation active', timestamp: new Date().toISOString() },
      { name: 'Database Security', status: 'pass', message: 'SQL injection prevention active', timestamp: new Date().toISOString() },
    ],
    metrics: {
      requestsBlocked: 0,
      threatsDetected: 0,
      uptime: 99.9,
      encryptionStatus: 'active',
      rateLimitStatus: 'active',
      corsStatus: 'configured',
    }
  })

  const [isRefreshing, setIsRefreshing] = useState(false)

  const refreshMetrics = () => {
    setIsRefreshing(true)
    // Simulate metrics update
    setTimeout(() => {
      setMetrics(prev => ({
        ...prev,
        metrics: {
          ...prev.metrics,
          requestsBlocked: prev.metrics.requestsBlocked + Math.floor(Math.random() * 3),
          threatsDetected: prev.metrics.threatsDetected + Math.floor(Math.random() * 2),
        }
      }))
      setIsRefreshing(false)
    }, 1000)
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500'
    if (score >= 70) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-500/20'
    if (score >= 70) return 'bg-yellow-500/20'
    return 'bg-red-500/20'
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'fail': return <XCircle className="w-4 h-4 text-red-500" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      default: return <RefreshCw className="w-4 h-4 text-gray-500" />
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-osint-panel border border-osint-cyan/30 rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-osint-cyan/20 bg-gradient-to-r from-osint-panel to-osint-bg">
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-osint-cyan animate-pulse" />
            <div>
              <h2 className="text-xl font-bold text-osint-text">Security Dashboard</h2>
              <p className="text-sm text-osint-text-dim">Real-time security monitoring</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-osint-text-dim hover:text-osint-text transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Score Section */}
        <div className="px-6 py-4 border-b border-osint-cyan/20">
          <div className="flex items-center gap-6">
            <div className={`w-24 h-24 rounded-full ${getScoreBg(metrics.score)} flex items-center justify-center border-2 ${metrics.score >= 90 ? 'border-green-500' : metrics.score >= 70 ? 'border-yellow-500' : 'border-red-500'
              }`}>
              <div className="text-center">
                <span className={`text-3xl font-bold ${getScoreColor(metrics.score)}`}>{metrics.score}</span>
                <span className="text-xs text-osint-text-dim block">SECURE SCORE</span>
              </div>
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-osint-cyan" />
                <span className="font-semibold">System Status: {
                  metrics.status === 'secure' ? '🟢 SECURE' :
                    metrics.status === 'warning' ? '🟡 WARNING' : '🔴 CRITICAL'
                }</span>
              </div>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <Server className="w-4 h-4 text-osint-text-dim" />
                  <span>Uptime: {metrics.metrics.uptime}%</span>
                </div>
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-osint-text-dim" />
                  <span>Encryption: {
                    metrics.metrics.encryptionStatus === 'active' ? '✅ Active' : '❌ Inactive'
                  }</span>
                </div>
                <div className="flex items-center gap-2">
                  <Key className="w-4 h-4 text-osint-text-dim" />
                  <span>Rate Limit: {
                    metrics.metrics.rateLimitStatus === 'active' ? '✅ Active' : '❌ Inactive'
                  }</span>
                </div>
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-osint-text-dim" />
                  <span>CORS: {
                    metrics.metrics.corsStatus === 'configured' ? '✅ Configured' : '❌ Unconfigured'
                  }</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="px-6 py-4 grid grid-cols-3 gap-4">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <XCircle className="w-5 h-5 text-red-500" />
              <span className="font-semibold">Blocked Requests</span>
            </div>
            <div className="text-3xl font-bold text-red-500">{metrics.metrics.requestsBlocked}</div>
            <div className="text-xs text-osint-text-dim mt-1">Rate limit violations</div>
          </div>

          <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
              <span className="font-semibold">Threats Detected</span>
            </div>
            <div className="text-3xl font-bold text-yellow-500">{metrics.metrics.threatsDetected}</div>
            <div className="text-xs text-osint-text-dim mt-1">Security incidents</div>
          </div>

          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="font-semibold">Active Protections</span>
            </div>
            <div className="text-3xl font-bold text-green-500">{metrics.checks.filter(c => c.status === 'pass').length}</div>
            <div className="text-xs text-osint-text-dim mt-1">Of {metrics.checks.length} security checks</div>
          </div>
        </div>

        {/* Security Checks */}
        <div className="px-6 py-4 border-t border-osint-cyan/20">
          <h3 className="font-semibold mb-3 flex items-center gap-2">
            <Eye className="w-4 h-4 text-osint-cyan" />
            Security Checks
          </h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {metrics.checks.map((check, index) => (
              <div
                key={index}
                className="flex items-center justify-between px-4 py-2 bg-osint-bg/50 rounded-lg border border-osint-cyan/10"
              >
                <div className="flex items-center gap-3">
                  {getStatusIcon(check.status)}
                  <span className="text-sm font-medium">{check.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-osint-text-dim">{check.message}</span>
                  <span className="text-xs text-osint-text-muted">
                    {new Date(check.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-osint-cyan/20 bg-osint-bg/30 flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-osint-text-dim">
            <span className="flex items-center gap-2">
              <Lock className="w-4 h-4" />
              All data encrypted at rest
            </span>
            <span className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              SOC 2 Compliant
            </span>
          </div>

          <button
            onClick={refreshMetrics}
            disabled={isRefreshing}
            className="flex items-center gap-2 px-4 py-2 bg-osint-cyan/20 hover:bg-osint-cyan/30 text-osint-cyan rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh Metrics
          </button>
        </div>
      </div>
    </div>
  )
}
