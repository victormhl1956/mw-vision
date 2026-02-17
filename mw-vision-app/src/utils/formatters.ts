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
