/**
 * PM2 Ecosystem Configuration for MW-Vision
 * Ensures all services auto-restart and stay alive
 *
 * Install: npm install -g pm2 pm2-windows-startup
 * Usage:
 *   pm2 start ecosystem.config.js
 *   pm2 save
 *   pm2 startup (for auto-start on boot)
 */

module.exports = {
  apps: [
    // Backend FastAPI
    {
      name: 'mw-vision-backend',
      script: 'python',
      args: 'main_modular.py',
      cwd: './backend',
      instances: 1,
      autorestart: true,
      watch: false,  // uvicorn has --reload
      max_restarts: 50,
      restart_delay: 5000,  // 5 seconds
      exp_backoff_restart_delay: 1000,  // Exponential backoff from 1s
      min_uptime: '30s',  // Consider successful if runs >30s
      error_file: './logs/pm2-backend-error.log',
      out_file: './logs/pm2-backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      env: {
        NODE_ENV: 'development',
        PORT: 8000,
        PYTHONUNBUFFERED: '1',  // Prevent output buffering
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 8000,
      },
    },

    // Frontend Vite Dev Server
    {
      name: 'mw-vision-frontend',
      script: 'C:\\Program Files\\nodejs\\node.exe',
      args: 'node_modules\\vite\\bin\\vite.js --port 5189 --host',
      cwd: './mw-vision-app',
      exec_mode: 'fork',
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 50,
      restart_delay: 5000,
      exp_backoff_restart_delay: 1000,
      min_uptime: '30s',
      error_file: './logs/pm2-frontend-error.log',
      out_file: './logs/pm2-frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      env: {
        PORT: 5189,
      },
    },

    // Health Monitor
    {
      name: 'mw-vision-health-monitor',
      script: 'python',
      args: 'health_monitor.py',
      cwd: './backend/scripts',
      instances: 1,
      autorestart: true,
      watch: false,
      max_restarts: 100,  // Should never die
      restart_delay: 30000,  // 30s delay (it's just monitoring)
      exp_backoff_restart_delay: 5000,
      min_uptime: '60s',
      error_file: './logs/pm2-health-error.log',
      out_file: './logs/pm2-health-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      env: {
        CHECK_INTERVAL: 60,  // 60 seconds between checks
      },
    },
  ],
}
