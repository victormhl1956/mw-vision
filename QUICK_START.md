# MW-Vision - Quick Start Guide

## 🚀 Acceso a la Aplicación

### ⚠️ IMPORTANTE: Arquitectura de Puertos

MW-Vision usa una arquitectura **separada** de Backend + Frontend:

| Servicio | Puerto | URL | Propósito |
|----------|--------|-----|-----------|
| **Frontend (UI)** | 5189 | http://localhost:5189/ | **ACCEDER AQUÍ** para la interfaz gráfica |
| **Backend (API)** | 8000 | http://localhost:8000/ | Solo API REST + WebSocket |

### ✅ Cómo Acceder a MW-Vision

**Para usar MW-Vision, abrir en el navegador:**

```
http://localhost:5189/
```

**NO abrir:** http://localhost:8000/ (es solo API, redirigirá al frontend)

---

## 📦 Servicios PM2

MW-Vision corre 3 servicios via PM2:

```bash
pm2 list
```

| Nombre | Descripción | Puerto |
|--------|-------------|--------|
| `mw-vision-backend` | FastAPI + WebSocket | 8000 |
| `mw-vision-frontend` | Vite + React UI | 5189 |
| `mw-vision-health-monitor` | Watchdog de servicios | - |

---

## 🔧 Comandos Útiles

### Iniciar Servicios

```bash
# Opción 1: Usar script de inicio
cd L:\nicedev-Project\MW-Vision
start_all.bat

# Opción 2: PM2 directo
pm2 start ecosystem.config.js
```

### Ver Estado

```bash
# Lista de servicios
pm2 list

# Logs en vivo
pm2 logs

# Logs de un servicio específico
pm2 logs mw-vision-frontend
pm2 logs mw-vision-backend
```

### Reiniciar

```bash
# Reiniciar todos
pm2 restart all

# Reiniciar uno específico
pm2 restart mw-vision-frontend
pm2 restart mw-vision-backend
```

### Detener

```bash
# Detener todos
pm2 stop all

# Detener uno específico
pm2 stop mw-vision-frontend
```

---

## 🐛 Troubleshooting

### Problema: "La UI no carga"

**Verificar:**

1. **¿Estás en el puerto correcto?**
   ```
   ✅ CORRECTO: http://localhost:5189/
   ❌ INCORRECTO: http://localhost:8000/
   ```

2. **¿El frontend está corriendo?**
   ```bash
   pm2 logs mw-vision-frontend --lines 20
   ```
   Debe mostrar: `VITE v6.x.x ready in XXX ms`

3. **¿Vite está realmente activo?**
   ```bash
   pm2 list
   # Buscar mw-vision-frontend
   # Memoria debe ser ~90-100mb (vs ~5mb si no corre Vite)
   ```

4. **Verificar endpoint:**
   ```bash
   curl http://localhost:5189/
   # Debe devolver HTML
   ```

### Problema: "Backend no responde"

```bash
# Ver logs
pm2 logs mw-vision-backend --lines 50

# Verificar health
curl http://localhost:8000/health

# Reiniciar
pm2 restart mw-vision-backend
```

### Problema: "WebSocket no conecta"

Verificar en logs del frontend:
```bash
pm2 logs mw-vision-frontend
# Buscar errores de WebSocket
```

El WebSocket debe conectar a: `ws://localhost:8000/ws`

---

## 📊 Endpoints del Backend

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Página de redirección al frontend |
| `/api` | GET | Información de la API (JSON) |
| `/health` | GET | Health check |
| `/ws` | WebSocket | Conexión WebSocket |
| `/api/agents` | GET/POST | Gestión de agentes |
| `/api/crew` | GET/POST | Control de crew |
| `/api/security` | GET | Métricas de seguridad |

---

## 🔍 Verificación Rápida

```bash
# 1. Verificar servicios PM2
pm2 list | grep "mw-vision"

# 2. Verificar backend (debe retornar JSON)
curl http://localhost:8000/health

# 3. Verificar frontend (debe retornar HTML)
curl http://localhost:5189/ | head -10

# 4. Abrir en navegador
start http://localhost:5189/
```

---

## 📁 Estructura del Proyecto

```
MW-Vision/
├── backend/              # FastAPI backend (puerto 8000)
│   ├── main_modular.py   # Entry point
│   ├── core/             # App factory
│   ├── modules/          # Módulos (websocket, crew, agents, security)
│   ├── routers/          # API routes
│   └── scripts/          # Health monitor, port monitor
│
├── mw-vision-app/        # React + Vite frontend (puerto 5189)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── views/
│   │   ├── services/
│   │   └── stores/
│   └── vite.config.ts
│
├── ecosystem.config.js   # Configuración PM2
├── install_services.bat  # Instalación de servicios
├── start_all.bat         # Inicio rápido
└── logs/                 # Logs de PM2
```

---

## 🎯 Workflow Típico

1. **Iniciar servicios:**
   ```bash
   cd L:\nicedev-Project\MW-Vision
   start_all.bat
   ```

2. **Abrir navegador:**
   ```
   http://localhost:5189/
   ```

3. **Monitorear:**
   ```bash
   pm2 monit
   # O
   pm2 logs
   ```

4. **Desarrollar:**
   - Frontend: Editar archivos en `mw-vision-app/src/`
   - Backend: Editar archivos en `backend/`
   - Hot reload activo en ambos

5. **Detener al finalizar:**
   ```bash
   pm2 stop all
   ```

---

## 📚 Documentación Adicional

- **Persistencia de Servicios:** `SERVICE_PERSISTENCE_GUIDE.md`
- **Reporte de Implementación:** `SERVER_PERSISTENCE_IMPLEMENTATION_REPORT.md`
- **Auditoría DEEPEX:** `DEEPEX_CONSOLIDATED_AUDIT_REPORT.md`
- **Reporte de Sesión:** `FINAL_SESSION_REPORT.md`

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa `pm2 logs` para errores
2. Consulta `SERVICE_PERSISTENCE_GUIDE.md` sección Troubleshooting
3. Verifica que estés accediendo al puerto correcto (5189, no 8000)
4. Asegúrate de que ambos servicios estén "online" en `pm2 list`

---

**Creado:** 2026-02-16
**Versión MW-Vision:** 3.0.0
**Estado:** ✅ Production-Ready
