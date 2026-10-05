/**
 * Utility functions for formatting data in MW-Vision
 */

/**
 * Format cost to $X.XX format (always 2 decimals)
 */
export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`;
}

/**
 * Format response time appropriately
 */
export function formatResponseTime(seconds: number): string {
  if (seconds === 0) return '0.0s';
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
  return `${seconds.toFixed(2)}s`;
}

/**
 * Format timestamp to human-readable time
 */
export function formatTime(timestamp: string | Date): string {
  const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
  return date.toLocaleTimeString();
}


/**
 * Una marca de tiempo que puede no existir.
 *
 * El backend devuelve `last_update: null` para un agente que no ha hecho nada
 * todavía, y `new Date('').toLocaleString()` pinta «Invalid Date». Eso no es un
 * error del usuario ni un fallo del sistema: es que no ha pasado nada. Decirlo
 * cuesta una línea y evita que alguien busque un defecto que no existe.
 */
export function formatearMomento(valor?: string | null,
                                 soloHora = false): string {
  if (!valor) return 'sin actividad'
  const d = new Date(valor)
  if (Number.isNaN(d.getTime())) return 'fecha ilegible'
  return soloHora ? d.toLocaleTimeString() : d.toLocaleString()
}
