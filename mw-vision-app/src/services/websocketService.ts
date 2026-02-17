import { useCrewStore, type ConnectionStatus } from '../stores/crewStore';

interface WebSocketMessage {
  type: string;
  agentId?: string;
  agent_id?: string;
  data?: any;
  agent?: any;
  decision?: any;
  timestamp?: number;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private currentUrl: string = '';
  private connectionStatus: ConnectionStatus = 'disconnected';
  private simulationInterval: any = null;

  connect(url: string = 'ws://localhost:8000/ws') {
    this.currentUrl = url;
    this.connectionStatus = 'connecting';
    this.updateStatus();
    try {
      this.ws = new WebSocket(url);
      this.ws.onopen = () => {
        this.connectionStatus = 'connected';
        this.updateStatus();
        if (this.simulationInterval) clearInterval(this.simulationInterval);
      };
      this.ws.onmessage = (event) => {
        const msg: WebSocketMessage = JSON.parse(event.data);
        const store = useCrewStore.getState();
        const id = msg.agentId || msg.agent_id || (msg.agent && msg.agent.id);

        switch (msg.type) {
          case 'agent_status':
          case 'agent_update':
            if (id) store.updateAgentStatus(id, (msg.data?.status || (msg.agent && msg.agent.status) || 'idle') as any);
            break;
          case 'cost_update':
            if (id && msg.data?.cost !== undefined) store.updateAgentCost(id, msg.data.cost);
            break;
        }
      };
      this.ws.onclose = () => {
        this.connectionStatus = 'disconnected';
        this.updateStatus();
        this.scheduleReconnect();
      };
    } catch {
      this.startSimulation();
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect() {
    if (this.connectionStatus === 'disconnected') {
      setTimeout(() => this.connect(this.currentUrl), 1000);
    }
  }

  private updateStatus() {
    useCrewStore.getState().setConnectionStatus(this.connectionStatus);
  }

  private startSimulation() {
    this.connectionStatus = 'simulating';
    this.updateStatus();
    this.simulationInterval = setInterval(() => {
      const store = useCrewStore.getState();
      if (!store.isCrewRunning) return;
      store.agents.forEach(a => {
        if (a.status === 'running') store.updateAgentCost(a.id, a.totalCost + 0.001);
      });
    }, 2000);
  }

  send(msg: any) {
    if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(msg));
  }

  disconnect() {
    this.ws?.close();
    if (this.simulationInterval) clearInterval(this.simulationInterval);
  }
}

export const wsService = new WebSocketService();
export const connectToBackend = (url?: string) => wsService.connect(url);
export const disconnectFromBackend = () => wsService.disconnect();
export const sendCrewCommand = (command: string) => wsService.send({ type: 'crew_command', data: { command } });
export const sendAgentCommand = (agentId: string, command: string) => wsService.send({ type: 'agent_command', agentId, data: { command } });
