# MW-VISION: TODO LIST PARA BETA TESTER

**Generado:** 2026-02-16
**Por:** DEEPEX Audit (Claude + DeepSeek) + Manual Analysis
**Estado Actual:** 48% → Meta Beta: 75%
**Reporte Consolidado:** `DEEPEX_CONSOLIDATED_AUDIT_REPORT.md`

---

## 🚨 PRIORIDAD URGENTE: BUGS DE INTEGRACIÓN (DeepSeek Findings)

### 0. WebSocket Protocol Fixes [2 días] ⚠️ BLOQUEADOR
**Estos bugs impiden que frontend y backend se comuniquen correctamente**

- [ ] 0.1 **HIGH** Fix WebSocket type mismatch
  - `websocketService.ts:345` cambiar `crew_status` → `crew_command`
  - `websocketService.ts:352` cambiar `agent_update` → `agent_command`
- [ ] 0.2 **HIGH** Fix field naming mismatch (snake_case ↔ camelCase)
  - Backend envía `agent_id`, `is_running`
  - Frontend espera `agentId`, `isRunning`
  - Normalizar en parser o ajustar uno de los lados
- [ ] 0.3 **HIGH** Eliminar doble inicialización WebSocket
  - `websocketService.ts:331` - auto-connect al importar
  - `App.tsx:34` - connect en useEffect
  - Mantener solo UNO
- [ ] 0.4 **HIGH** Reemplazar sync XHR por fetch async
  - `websocketService.ts:36-37` y `54-55`
  - Usar fetch + AbortController con timeout

**Archivos:** `websocketService.ts`, `App.tsx`, `main.py`

---

## PRIORIDAD CRÍTICA (Bloqueadores)

### 1. Backend Real con CrewAI Integration [5 días]
- [ ] 1.1 Integrar CrewAI real para ejecución de agentes
- [ ] 1.2 Implementar Agent Registry dinámico
- [ ] 1.3 Conectar con modelos reales (Claude, GPT-4o, DeepSeek)
- [ ] 1.4 Implementar task queue para workflows
- [ ] 1.5 Real-time token counting y cost calculation

**Archivos:** `backend/main.py`, nuevo `backend/services/crewai_engine.py`

### 2. Database Persistence [3 días]
- [ ] 2.1 Implementar SQLite para MVP
- [ ] 2.2 Crear tablas: workflows, executions, agent_logs, recovery_events
- [ ] 2.3 CRUD completo de proyectos
- [ ] 2.4 Persistir historial de ejecuciones
- [ ] 2.5 Export/Import de workflows (JSON)

**Archivos:** nuevo `backend/database/`, `backend/models/`

### 3. GitHub Integration Real [4 días]
- [ ] 3.1 Implementar GitHub OAuth flow
- [ ] 3.2 API para clonar repositorios (local y remoto)
- [ ] 3.3 Real file analysis con AST parsing
- [ ] 3.4 Dependency graph extraction
- [ ] 3.5 Webhook integration para cambios en repo
- [ ] 3.6 Soporte para repos privados

**Archivos:** `BlueprintView.tsx`, nuevo `backend/services/github_service.py`

### 4. Multi-Project System [3 días]
- [ ] 4.1 Project CRUD (create, read, update, delete)
- [ ] 4.2 Soporte para proyectos locales (path en disco)
- [ ] 4.3 Soporte para proyectos remotos (GitHub URL)
- [ ] 4.4 Project templates (OSINT, Web App, CLI Tool)
- [ ] 4.5 Project switching sin pérdida de estado
- [ ] 4.6 Project versioning y snapshots

**Archivos:** `crewStore.ts`, nuevo `projectStore.ts`

---

## PRIORIDAD ALTA

### 5. AI Tester / Browser Testing Real [4 días]
**Estado actual:** `browserInteractor.ts` existe pero es simulación

- [ ] 5.1 Integrar Chrome DevTools MCP
- [ ] 5.2 Implementar visual regression testing
- [ ] 5.3 Screenshot capture en cada step
- [ ] 5.4 Real DOM verification
- [ ] 5.5 Test report generation con evidencia
- [ ] 5.6 Playwright integration para E2E
- [ ] 5.7 Selector auto-discovery

### 6. Multi-Mode Execution [2 días]
- [ ] 6.1 DRY_RUN mode - Solo validar
- [ ] 6.2 SAFE_MODE - Human-in-the-loop
- [ ] 6.3 AUTONOMOUS - Actual
- [ ] 6.4 ITERATIVE - Multi-iteration
- [ ] 6.5 Mode selector en UI
- [ ] 6.6 Checkpoints y rollback

### 7. Workflow Auto-Recovery [2 días]
- [ ] 7.1 Retry con exponential backoff
- [ ] 7.2 Model fallback automático
- [ ] 7.3 Rate limit detection
- [ ] 7.4 Memory error handling
- [ ] 7.5 Recovery event logging

### 8. Testing Suite [3 días]
- [ ] 8.1 Setup Vitest
- [ ] 8.2 Setup Playwright
- [ ] 8.3 Tests para stores
- [ ] 8.4 Tests para services
- [ ] 8.5 Tests para backend
- [ ] 8.6 CI/CD con GitHub Actions
- [ ] 8.7 Coverage >60%

---

## PRIORIDAD MEDIA

### 9. Authentication [3 días]
- [ ] 9.1 JWT authentication
- [ ] 9.2 Login/Register UI
- [ ] 9.3 Session management
- [ ] 9.4 Role-based access
- [ ] 9.5 API key management

### 10. Visual Report Generator [2 días]
- [ ] 10.1 Execution summary (PDF/HTML)
- [ ] 10.2 Cost breakdown
- [ ] 10.3 Timeline visualization
- [ ] 10.4 Error analysis
- [ ] 10.5 Export Markdown

### 11. Docker Deployment [2 días]
- [ ] 11.1 Dockerfile backend
- [ ] 11.2 Dockerfile frontend
- [ ] 11.3 docker-compose.yml
- [ ] 11.4 Environment variables
- [ ] 11.5 Health checks
- [ ] 11.6 Volume persistence

---

## PRIORIDAD BAJA

### 12. Chrome DevTools MCP Full [4 días]
- [ ] 12.1 Integrar 26 herramientas MCP
- [ ] 12.2 Console capture
- [ ] 12.3 Network monitoring
- [ ] 12.4 DOM manipulation
- [ ] 12.5 Performance profiling

### 13. Advanced Analytics [2 días]
- [ ] 13.1 Cost trends
- [ ] 13.2 Agent metrics
- [ ] 13.3 Success rate
- [ ] 13.4 Token analytics

### 14. Mobile PWA [2 días]
- [ ] 14.1 Service worker
- [ ] 14.2 Manifest.json
- [ ] 14.3 Offline capability
- [ ] 14.4 Push notifications

---

## ROADMAP SUGERIDO

| Sprint | Semana | Tasks | Días |
|--------|--------|-------|------|
| 1 | 1-2 | Backend + DB + Tests | 10 |
| 2 | 3-4 | GitHub + Projects + Modes | 9 |
| 3 | 5 | AI Tester + Recovery + Docker | 8 |
| 4 | 6 | Auth + Reports + QA | 8 |

**Total estimado:** 35-41 días para Beta Ready

---

## NOTAS IMPORTANTES

1. **AI Tester ya existe** en `browserInteractor.ts` pero es simulación
2. **Documentación es excelente** - 90% de features están documentadas
3. **El gap principal** es backend real vs mock data
4. **Para trabajar como Jules/Codex** necesita GitHub Integration real

---

## REFERENCIAS

- `docs/MW-VISION-TECHNICAL-SPECIFICATION.md` - Spec completa
- `docs/CHROME_DEVTOOLS_MCP_DEEPEX_ANALYSIS.md` - 26 tools MCP
- `docs/Hydra-Protocol.md` - IP protection
- `docs/ALPHA_TESTING_READINESS_REPORT.md` - Estado actual
- `DEEPEX_AUDIT_20260215_201614.md` - Audit report
