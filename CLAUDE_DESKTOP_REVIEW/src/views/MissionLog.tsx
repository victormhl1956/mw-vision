import { useEffect, useRef } from 'react';
import { Terminal, Activity, Zap, CheckCircle } from 'lucide-react';
import { useCrewStore } from '../stores/crewStore';

export default function MissionLog() {
  const { missionLogs } = useCrewStore();
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [missionLogs]);

  const getLogStyle = (level: string) => {
    switch (level) {
      case 'INFO':
        return { borderLeftColor: '#00d9ff', color: '#00d9ff' };
      case 'WARNING':
        return { borderLeftColor: '#ffbe0b', color: '#ffbe0b' };
      case 'SUCCESS':
        return { borderLeftColor: '#39ff14', color: '#39ff14' };
      case 'ERROR':
        return { borderLeftColor: '#ff003c', color: '#ff003c' };
      default:
        return { borderLeftColor: '#8892a6', color: '#8892a6' };
    }
  };

  const getIcon = (level: string) => {
    switch (level) {
      case 'INFO': return <Zap className="w-4 h-4" />;
      case 'WARNING': return <Activity className="w-4 h-4" />;
      case 'SUCCESS': return <CheckCircle className="w-4 h-4" />;
      case 'ERROR': return <Terminal className="w-4 h-4" />;
      default: return <Terminal className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex flex-col h-[600px] glass-panel rounded-lg overflow-hidden border border-osint-cyan/30">
      <div className="p-4 border-b border-osint-cyan/20 bg-osint-panel/50 flex justify-between items-center">
        <h2 className="text-xl font-orbitron font-bold text-osint-cyan flex items-center gap-2">
          <Terminal className="w-5 h-5 text-osint-cyan" />
          Mission Log
        </h2>
        <div className="text-xs text-osint-text-dim font-mono animate-pulse">
          LISTENING_FOR_STRATEGIC_TELEMETRY...
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-black/40 font-mono text-sm leading-relaxed">
        {missionLogs.map((log, i) => (
          <div
            key={i}
            className="flex gap-4 p-3 border-l-4 bg-osint-panel/30 rounded-r transition-all hover:bg-osint-panel/50"
            style={getLogStyle(log.level)}
          >
            <div className="flex-shrink-0 mt-1">
              {getIcon(log.level)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-baseline mb-1">
                <span className="text-[10px] uppercase font-bold tracking-widest opacity-60">
                  [{log.level}]
                </span>
                <span className="text-[10px] opacity-40">
                  {log.timestamp}
                </span>
              </div>
              <div className="text-osint-text">
                {log.message}
              </div>
            </div>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
