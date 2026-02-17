# MW-Vision Service Persistence Guide

**Problema resuelto:** Backend (puerto 8000) y Frontend (puerto 5189) se caían aleatoriamente y no se reiniciaban automáticamente.

**Solución aplicada:** Sistema de persistencia multi-capa basado en PM2 + Health Monitoring (arquitectura probada en OSINT-MW).

---

## Arquitectura de Persistencia

```
┌─────────────────────────────────────────────────────────────┐
│                  CAPA 1: PM2 Process Manager                │
│  - Auto-restart on crash                                    │
│  - Exponential backoff                                      │
│  - Max 50 restarts per service                              │
│  - Startup on Windows boot                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CAPA 2: Health Monitor (HTTP Checks)           │
│  - Checks /health endpoints every 60s                       │
│  - Triggers PM2 restart after 3 failures                    │
│  - Logs all health events                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CAPA 3: Port Monitor (TCP Checks)              │
│  - Checks if ports 8000/5189 are listening every 30s        │
│  - Triggers PM2 restart after 3 failures                    │
│  - Complementary to health monitor                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Instalación

### 1. Instalar servicios

Ejecutar como **Administrador** (para configurar auto-start en boot):

```cmd
cd L:\nicedev-Project\MW-Vision
install_services.bat
```

Esto hace:
1. Verifica Node.js instalado
2. Instala PM2 globalmente si no existe
3. Crea directorio de logs
4. Inicia backend, frontend, y health monitor via PM2
5. Guarda configuración de PM2
6. Configura auto-start en Windows boot

### 2. Verificar servicios

```cmd
pm2 list
```

Deberías ver:

| Name | Status | Restarts | Uptime |
|------|--------|----------|--------|
| mw-vision-backend | online | 0 | 5m |
| mw-vision-frontend | online | 0 | 5m |
| mw-vision-health-monitor | online | 0 | 5m |

### 3. Probar endpoints

- Backend: http://localhost:8000/health
- Frontend: http://localhost:5189/

---

## Uso Diario

### Iniciar servicios

```cmd
cd L:\nicedev-Project\MW-Vision
start_all.bat
```

O manualmente:
```cmd
pm2 start ecosystem.config.js
```

### Ver logs en vivo

```cmd
pm2 logs
```

O logs específicos:
```cmd
pm2 logs mw-vision-backend
pm2 logs mw-vision-frontend
pm2 logs mw-vision-health-monitor
```

### Reiniciar servicios

```cmd
pm2 restart all
```

O uno específico:
```cmd
pm2 restart mw-vision-backend
```

### Detener servicios

```cmd
pm2 stop all
```

### Monitorear recursos

```cmd
pm2 monit
```

---

## Archivos Clave

| Archivo | Descripción |
|---------|-------------|
| `ecosystem.config.js` | Configuración PM2 (puertos, rutas, restart policy) |
| `backend/scripts/health_monitor.py` | Monitor HTTP de /health endpoints |
| `backend/scripts/port_monitor.py` | Monitor TCP de puertos 8000/5189 |
| `install_services.bat` | Script de instalación completo |
| `start_all.bat` | Script de inicio rápido |
| `logs/pm2-backend-*.log` | Logs de backend |
| `logs/pm2-frontend-*.log` | Logs de frontend |
| `logs/pm2-health-*.log` | Logs de health monitor |
| `backend/logs/health_monitor.log` | Logs internos del health monitor |
| `backend/logs/port_monitor.log` | Logs internos del port monitor |

---

## Configuración de PM2

### Backend (FastAPI)

```javascript
{
  name: 'mw-vision-backend',
  script: 'python',
  args: 'main_modular.py',
  cwd: './backend',
  autorestart: true,
  max_restarts: 50,
  restart_delay: 5000,  // 5 segundos
  exp_backoff_restart_delay: 1000,  // Backoff exponencial desde 1s
  min_uptime: '30s',  // Considera exitoso si corre >30s
  env: {
    PORT: 8000,
    PYTHONUNBUFFERED: '1',  // Evita buffering de output
  },
}
```

### Frontend (Vite)

```javascript
{
  name: 'mw-vision-frontend',
  script: 'npm',
  args: 'run dev',
  cwd: './mw-vision-app',
  autorestart: true,
  max_restarts: 50,
  restart_delay: 5000,
  env: {
    PORT: 5189,
  },
}
```

### Health Monitor

```javascript
{
  name: 'mw-vision-health-monitor',
  script: 'python',
  args: 'health_monitor.py',
  cwd: './backend/scripts',
  autorestart: true,
  max_restarts: 100,  // El monitor nunca debe morir
  restart_delay: 30000,  // 30s delay (solo monitorea)
  env: {
    CHECK_INTERVAL: 60,  // 60 segundos entre checks
  },
}
```

---

## Health Monitor

### Servicios monitoreados

```python
SERVICES = {
    "mw-vision-backend": {
        "url": "http://localhost:8000/health",
        "pm2_name": "mw-vision-backend",
        "critical": True,
        "timeout": 5,
    },
    "mw-vision-frontend": {
        "url": "http://localhost:5189/",
        "pm2_name": "mw-vision-frontend",
        "critical": True,
        "timeout": 5,
    },
}
```

### Política de restart

- Hace HTTP GET cada 60 segundos
- Si falla 3 veces consecutivas → `pm2 restart <service>`
- Reset counter después de restart exitoso
- Guarda status en `health_status.json`

---

## Port Monitor

### Puertos monitoreados

- Backend: `8000`
- Frontend: `5189`

### Política de restart

- Verifica que el puerto esté escuchando (TCP) cada 30 segundos
- Si falla 3 veces consecutivas → `pm2 restart <service>`
- Complementa al health monitor (verifica capa TCP vs HTTP)

---

## Troubleshooting

### Problema: "PM2 not found"

Instalar PM2:
```cmd
npm install -g pm2 pm2-windows-startup
```

### Problema: Backend no inicia

Ver logs:
```cmd
pm2 logs mw-vision-backend --lines 50
```

Verificar dependencias:
```cmd
cd backend
pip install -r requirements.txt
```

### Problema: Frontend no inicia

Ver logs:
```cmd
pm2 logs mw-vision-frontend --lines 50
```

Verificar dependencias:
```cmd
cd mw-vision-app
npm install
```

### Problema: Frontend "online" pero no despliega UI

**Síntoma:** PM2 muestra el frontend como "online" pero la UI no carga en el navegador.

**Diagnóstico:**
```cmd
# Verificar si Vite realmente está corriendo
pm2 logs mw-vision-frontend --lines 20

# Buscar mensaje "VITE v6.x.x ready in XXX ms"
# Si NO aparece, Vite no está corriendo
```

**Causa:** El batch wrapper (`start_frontend.bat`) se ejecutó pero terminó inmediatamente debido a `cmd.exe /c`.

**Solución:** Usar node directamente con vite.js (ya implementado en ecosystem.config.js):
```javascript
{
  name: 'mw-vision-frontend',
  script: 'C:\\Program Files\\nodejs\\node.exe',
  args: 'node_modules\\vite\\bin\\vite.js --port 5189 --host',
  cwd: './mw-vision-app',
  exec_mode: 'fork',
  // ... rest of config
}
```

Reiniciar frontend:
```cmd
pm2 delete mw-vision-frontend
pm2 start ecosystem.config.js --only mw-vision-frontend
pm2 save
```

**Verificación exitosa:**
- `pm2 logs mw-vision-frontend` debe mostrar "VITE v6.x.x ready"
- Memoria del proceso debe ser ~90-100mb (vs ~5mb cuando no corre Vite)
- http://localhost:5189/ debe cargar la UI de React

### Problema: Servicios no se reinician automáticamente

Verificar health monitor:
```cmd
pm2 logs mw-vision-health-monitor
```

Verificar que PM2 esté guardado:
```cmd
pm2 save
```

### Problema: Auto-start en boot no funciona

Ejecutar como **Administrador**:
```cmd
pm2-startup install
pm2 save
```

---

## Comparación con OSINT-MW

MW-Vision usa la **misma arquitectura** probada en OSINT-MW:

| Componente | OSINT-MW | MW-Vision |
|------------|----------|-----------|
| **Process Manager** | PM2 | PM2 ✅ |
| **Health Monitor** | HTTP checks + PM2 restart | HTTP checks + PM2 restart ✅ |
| **Port Monitor** | TCP checks + PM2 restart | TCP checks + PM2 restart ✅ |
| **Auto-start on boot** | Windows Scheduled Task | PM2 startup ✅ |
| **Restart Policy** | Exponential backoff | Exponential backoff ✅ |
| **Max Restarts** | 50 per service | 50 per service ✅ |

---

## Logs de Actividad

### Backend logs
```
logs/pm2-backend-out.log   - stdout (print, logger.info)
logs/pm2-backend-error.log - stderr (exceptions, logger.error)
```

### Frontend logs
```
logs/pm2-frontend-out.log   - stdout (console.log)
logs/pm2-frontend-error.log - stderr (errors)
```

### Health monitor logs
```
logs/pm2-health-out.log        - PM2 stdout
logs/pm2-health-error.log      - PM2 stderr
backend/logs/health_monitor.log - Internal logs
```

### Port monitor logs
```
backend/logs/port_monitor.log - Internal logs
```

---

## Estado de Servicios

El health monitor guarda estado en `health_status.json`:

```json
{
  "timestamp": "2026-02-16T14:30:00",
  "services": {
    "mw-vision-backend": {
      "status": "healthy",
      "last_check": "2026-02-16T14:30:00",
      "failures": 0
    },
    "mw-vision-frontend": {
      "status": "healthy",
      "last_check": "2026-02-16T14:30:00",
      "failures": 0
    }
  }
}
```

Esto permite monitoreo externo o dashboards.

---

## Próximos Pasos (Opcional)

Para aumentar resiliencia aún más:

1. **Anti-Freeze Watchdog** - Detecta procesos "zombie" (consumo CPU 0% por >5 min)
2. **Startup Sequence Controller** - Asegura orden de inicio (backend → frontend)
3. **Windows Task Scheduler** - Fallback si PM2 falla
4. **Email/SMS Alerts** - Notificaciones de caídas críticas
5. **Metrics Collection** - Prometheus/Grafana para monitoreo

---

## Referencias

- **PM2 Docs**: https://pm2.keymetrics.io/docs/usage/quick-start/
- **PM2 Windows Startup**: https://www.npmjs.com/package/pm2-windows-startup
- **OSINT-MW Implementation**: `L:\nicedev-Project\OSINT-MW\backend\scripts\health_monitor.py`

---

**Creado:** 2026-02-16
**Basado en:** Solución probada en OSINT-MW (días de desarrollo)
**Estado:** ✅ LISTO PARA PRODUCCIÓN
