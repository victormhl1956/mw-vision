/**
 * The one place that builds a WebSocket URL.
 *
 * Two defects this replaces:
 *
 * 1. `ws://localhost:8000/ws` was hardcoded in useWebSocket.ts and
 *    websocketService.ts, so `VITE_WS_BASE` — documented in .env.example for
 *    Tailscale access — was never read. Remote access could not work for the
 *    WebSocket, only for the REST API.
 * 2. The backend now authenticates /ws (it served any connection before), so
 *    the token has to travel with every connection.
 */

const DEFAULT_BASE = 'ws://localhost:8000';

const base = (import.meta.env.VITE_WS_BASE ?? DEFAULT_BASE).replace(/\/+$/, '');
const token = (import.meta.env.VITE_WS_TOKEN ?? '').trim();

/** True when a token is configured. Lets the UI explain a refusal. */
export const hasWsToken = token.length > 0;

/**
 * Build the URL for a WebSocket path.
 *
 * A missing token is reported out loud rather than producing a silent refusal:
 * without this, the backend closes the connection with 1008 and the UI shows
 * "disconnected" with no cause, which is how a configuration problem gets
 * mistaken for a network problem.
 */
export function wsUrl(path: string = '/ws'): string {
  const url = `${base}${path.startsWith('/') ? path : `/${path}`}`;
  if (!hasWsToken) {
    console.error(
      '[ws] VITE_WS_TOKEN is not set, so the backend will refuse this ' +
        'connection with code 1008. Mint one on the server with: ' +
        'python backend/scripts/issue_ws_token.py',
    );
    return url;
  }
  return `${url}?token=${encodeURIComponent(token)}`;
}
