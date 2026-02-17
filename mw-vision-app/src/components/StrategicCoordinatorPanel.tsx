import { useCrewStore } from '../stores/crewStore';

export function StrategicCoordinatorPanel() {
    const routingHistory = useCrewStore(state => state.routingHistory);

    return (
        <div style={{
            position: 'absolute',
            top: '80px',
            right: '20px',
            width: '350px',
            background: 'rgba(18, 24, 41, 0.95)',
            border: '1px solid #00d9ff',
            borderRadius: '8px',
            padding: '15px',
            maxHeight: '400px',
            overflowY: 'auto',
            zIndex: 10
        }}>
            <h3 style={{ color: '#00d9ff', marginBottom: '10px', fontFamily: 'Orbitron' }}>
                Strategic Coordinator Decisions
            </h3>
            {routingHistory.length === 0 ? (
                <div className="text-osint-text-dim text-sm italic">Waiting for decisions...</div>
            ) : (
                routingHistory.map((decision, i) => (
                    <div key={i} style={{
                        borderLeft: '3px solid ' + (decision.complexity < 5 ? '#39ff14' : '#ff006e'),
                        padding: '8px',
                        marginBottom: '8px',
                        background: 'rgba(0,0,0,0.3)',
                        borderRadius: '4px'
                    }}>
                        <div style={{ fontSize: '11px', color: '#8892a6' }}>
                            {new Date(decision.timestamp).toLocaleTimeString()}
                        </div>
                        <div style={{ fontSize: '13px', color: '#e0e6ed', marginTop: '4px' }}>
                            {decision.query.substring(0, 50)}...
                        </div>
                        <div style={{ fontSize: '12px', color: '#00d9ff', marginTop: '4px' }}>
                            Complexity: {decision.complexity}/10 → {decision.selectedModel}
                        </div>
                        <div style={{ fontSize: '11px', color: '#8892a6', marginTop: '4px' }}>
                            {decision.reasoning}
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}
