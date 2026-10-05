import { useState } from 'react'
import { GitBranch, FileCode, FolderTree, Shield, Loader2 } from 'lucide-react'
import { useToast } from '../components/Toast'

interface FileItem {
  path: string
  classification: 'proprietary' | 'public'
  lines: number
  hydraProtected?: boolean
}

// Lista de ejemplo. Se queda porque la vista no tiene de dónde sacar ficheros
// todavía, pero la interfaz lo DICE: ver el aviso de arriba del panel. Un dato
// de ejemplo sin etiqueta se lee como un inventario real.
const FICHEROS_DE_EJEMPLO: FileItem[] = [
  { path: 'src/auth/login.ts', classification: 'proprietary', lines: 234, hydraProtected: false },
  { path: 'src/utils/helpers.ts', classification: 'public', lines: 89 },
  { path: 'src/api/endpoints.ts', classification: 'proprietary', lines: 456, hydraProtected: false },
  { path: 'src/components/Button.tsx', classification: 'public', lines: 67 },
]

export default function BlueprintView() {
  const [files] = useState<FileItem[]>(FICHEROS_DE_EJEMPLO)
  const [repoUrl, setRepoUrl] = useState('')
  // Nada enciende estos dos, porque esta vista no procesa nada. Antes los
  // encendía un `setTimeout` que luego anunciaba un éxito que no había ocurrido.
  // Se quedan como constantes para que el tipado impida volver a engancharlos a
  // una espera falsa sin pensarlo.
  const isImporting = false
  const isHydraProcessing = false
  const { showToast } = useToast()

  const proprietaryCount = files.filter(f => f.classification === 'proprietary').length
  const publicCount = files.filter(f => f.classification === 'public').length
  const hydraProtectedCount = files.filter(f => f.hydraProtected).length

  const handleGitHubImport = async () => {
    if (!repoUrl.trim()) {
      showToast('warning', 'Please enter a GitHub repository URL')
      return
    }

    // Validate GitHub URL format
    const githubUrlPattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+/
    if (!githubUrlPattern.test(repoUrl)) {
      showToast('error', 'Invalid GitHub URL format')
      return
    }

    // Aquí había un `setTimeout` de 3 segundos que añadía cuatro ficheros
    // inventados y anunciaba «Imported 4 files from …». El botón de importar no
    // importaba nada y lo celebraba: eso no es una maqueta incompleta, es un
    // éxito falso, y quien lo ve actúa confiando en él.
    //
    // Mientras no haya backend que clone y analice el repositorio, lo que toca
    // es decirlo. La validación del URL de arriba sí es real y se queda.
    showToast(
      'warning',
      'La importación desde GitHub no está conectada todavía: no se ha ' +
      'importado nada. El URL tiene el formato correcto.',
      7000,
    )
    setRepoUrl('')
  }

  const handleHydraProtection = () => {
    const unprotectedProprietary = files.filter(
      f => f.classification === 'proprietary' && !f.hydraProtected
    )

    if (unprotectedProprietary.length === 0) {
      showToast('info', 'All proprietary files are already protected')
      return
    }

    // Aquí había un `setTimeout` de 2,5 segundos que marcaba todos los ficheros
    // propietarios como protegidos y anunciaba «Protected N proprietary files
    // with Hydra Protocol». No protegía nada.
    //
    // De todos los éxitos falsos de esta interfaz, este es el peor: el argumento
    // del producto es proteger código propietario, y quien ve ese mensaje deja
    // de preocuparse por unos ficheros que siguen expuestos. Un panel que miente
    // sobre un número molesta; un botón que miente sobre haber protegido algo
    // hace daño.
    showToast(
      'warning',
      `Hydra Protocol no está conectado desde esta vista: los ` +
      `${unprotectedProprietary.length} ficheros propietarios NO se han ` +
      `protegido.`,
      7000,
    )
  }

  return (
    <div className="space-y-6">
      {/* El aviso va ARRIBA y siempre visible. Los cuatro recuentos de abajo
          salen de una lista de ejemplo, y sin esta línea se leen como un
          inventario real del repositorio. */}
      <div className="glass-panel p-4 rounded-lg border border-osint-yellow/40 bg-osint-yellow/5">
        <div className="flex items-start gap-3">
          <Shield className="w-5 h-5 text-osint-yellow mt-0.5 shrink-0" />
          <div className="text-sm">
            <div className="font-semibold text-osint-yellow">
              Vista de ejemplo: no está conectada a ningún repositorio
            </div>
            <div className="text-osint-text-dim mt-1">
              Los {files.length} ficheros de abajo son datos de muestra. Importar
              desde GitHub y aplicar Hydra Protocol todavía no hacen nada, y lo
              dicen al pulsarlos en vez de anunciar un éxito que no ha ocurrido.
            </div>
          </div>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass-panel p-4 rounded-lg">
          <div className="flex items-center gap-3">
            <FolderTree className="w-8 h-8 text-osint-cyan" />
            <div>
              <div className="text-sm text-osint-text-dim">Total Files</div>
              <div className="text-2xl font-bold text-osint-text">{files.length}</div>
            </div>
          </div>
        </div>
        <div className="glass-panel p-4 rounded-lg">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-osint-red" />
            <div>
              <div className="text-sm text-osint-text-dim">Proprietary</div>
              <div className="text-2xl font-bold text-osint-red">{proprietaryCount}</div>
            </div>
          </div>
        </div>
        <div className="glass-panel p-4 rounded-lg">
          <div className="flex items-center gap-3">
            <FileCode className="w-8 h-8 text-osint-green" />
            <div>
              <div className="text-sm text-osint-text-dim">Public</div>
              <div className="text-2xl font-bold text-osint-green">{publicCount}</div>
            </div>
          </div>
        </div>
        <div className="glass-panel p-4 rounded-lg">
          <div className="flex items-center gap-3">
            <GitBranch className="w-8 h-8 text-osint-purple" />
            <div>
              <div className="text-sm text-osint-text-dim">Hydra Protected</div>
              <div className="text-2xl font-bold text-osint-purple">{hydraProtectedCount}</div>
            </div>
          </div>
        </div>
      </div>

      {/* GitHub Import */}
      <div className="glass-panel p-6 rounded-lg">
        <h2 className="text-xl font-orbitron font-bold text-osint-cyan mb-4">
          GitHub Repository Import
        </h2>
        <div className="flex gap-3">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleGitHubImport()}
            placeholder="https://github.com/username/repo-name (private repos need token)"
            className="flex-1 bg-osint-panel border border-osint-cyan/30 rounded-lg px-4 py-3 text-osint-text placeholder-osint-text-muted focus:outline-none focus:border-osint-cyan"
            disabled={isImporting}
          />
          <button 
            onClick={handleGitHubImport}
            disabled={isImporting}
            className="px-6 py-3 bg-osint-cyan/20 border border-osint-cyan text-osint-cyan rounded-lg hover:bg-osint-cyan/30 hover:shadow-[0_0_15px_rgba(0,212,255,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isImporting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Importing...
              </>
            ) : (
              'Import & Classify'
            )}
          </button>
        </div>
        <p className="text-sm text-osint-text-dim mt-3">
          Automatically clone, analyze AST, and classify files as public/proprietary
        </p>
      </div>

      {/* File Classification */}
      <div className="glass-panel p-6 rounded-lg">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-orbitron font-bold text-osint-cyan">
            Code Classification
          </h2>
          <button
            onClick={handleHydraProtection}
            disabled={isHydraProcessing || proprietaryCount === 0}
            className="px-4 py-2 bg-osint-purple/20 border border-osint-purple text-osint-purple rounded-lg hover:bg-osint-purple/30 hover:shadow-[0_0_15px_rgba(157,78,221,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm"
          >
            {isHydraProcessing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Protecting...
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                Apply Hydra Protection
              </>
            )}
          </button>
        </div>
        <div className="space-y-3">
          {files.map((file, idx) => (
            <div key={idx} className="glass-card p-4 rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1">
                <FileCode className="w-5 h-5 text-osint-cyan" />
                <div className="flex-1">
                  <div className="text-osint-text font-mono text-sm">{file.path}</div>
                  <div className="text-xs text-osint-text-dim mt-1">{file.lines} lines</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  file.classification === 'proprietary'
                    ? 'bg-osint-red/20 text-osint-red border border-osint-red'
                    : 'bg-osint-green/20 text-osint-green border border-osint-green'
                }`}>
                  {file.classification.toUpperCase()}
                </div>
                {file.hydraProtected && (
                  <div className="px-3 py-1 rounded-full text-xs font-semibold bg-osint-purple/20 text-osint-purple border border-osint-purple flex items-center gap-1">
                    <Shield className="w-3 h-3" />
                    PROTECTED
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Hydra Protocol Info */}
      <div className="glass-panel p-6 rounded-lg border-2 border-osint-purple/30">
        <div className="flex items-center gap-3 mb-4">
          <Shield className="w-6 h-6 text-osint-purple" />
          <h3 className="text-lg font-orbitron font-bold text-osint-purple">Hydra Protocol v2</h3>
          <div className={`ml-auto px-3 py-1 rounded-full text-xs font-semibold ${
            isHydraProcessing
              ? 'bg-osint-orange/20 text-osint-orange border border-osint-orange'
              : hydraProtectedCount > 0
              ? 'bg-osint-green/20 text-osint-green border border-osint-green'
              : 'bg-osint-panel border-osint-text-muted text-osint-text-muted'
          }`}>
            {isHydraProcessing ? 'PROCESSING' : hydraProtectedCount > 0 ? 'ACTIVE' : 'STANDBY'}
          </div>
        </div>
        <p className="text-osint-text-dim text-sm mb-4">
          Proprietary files will be fragmented, obfuscated, and protected when sent to untrusted models (DeepSeek, Qwen).
          Trust level determines protection intensity (0-4 scale).
        </p>
        <div className="grid grid-cols-3 gap-3 text-sm">
          <div className="p-3 bg-osint-panel/50 rounded border border-osint-purple/20">
            <div className="text-osint-purple font-semibold">Fragmentation</div>
            <div className="text-osint-text-dim text-xs mt-1">Code split into chunks</div>
          </div>
          <div className="p-3 bg-osint-panel/50 rounded border border-osint-purple/20">
            <div className="text-osint-purple font-semibold">Steganography</div>
            <div className="text-osint-text-dim text-xs mt-1">Hidden markers in comments</div>
          </div>
          <div className="p-3 bg-osint-panel/50 rounded border border-osint-purple/20">
            <div className="text-osint-purple font-semibold">Schema Rotation</div>
            <div className="text-osint-text-dim text-xs mt-1">Every ~50 requests</div>
          </div>
        </div>
      </div>
    </div>
  )
}