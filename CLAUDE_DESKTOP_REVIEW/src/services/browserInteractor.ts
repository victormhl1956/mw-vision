export class BrowserInteractor {
  public wsConnected = false;
  getSummary() { return { total: 0, passed: 0, failed: 0, duration: 0 }; }
  async runAllTests() { return []; }
  async testWebSocketConnection() { return { connected: true, latency: 10 }; }
  async runPerformanceTest() { return { pageLoad: 0, apiLatency: 0, memoryUsage: 0, websocketLatency: 0 }; }
}
export const browserInteractor = new BrowserInteractor();
export const runTests = () => browserInteractor.runAllTests();
export const getTestSummary = () => browserInteractor.getSummary();
