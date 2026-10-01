import { useEffect, useRef, useState } from 'react';
import { wsUrl } from '../services/wsUrl';

export function useWebSocket(onMessage: (data: any) => void) {
    const ws = useRef<WebSocket | null>(null);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        ws.current = new WebSocket(wsUrl('/ws'));

        ws.current.onopen = () => {
            console.log('WebSocket connected');
            setConnected(true);
        };

        ws.current.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        ws.current.onclose = () => {
            console.log('WebSocket disconnected');
            setConnected(false);
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        return () => {
            if (ws.current) {
                ws.current.close();
            }
        };
    }, [onMessage]);

    return { connected };
}
