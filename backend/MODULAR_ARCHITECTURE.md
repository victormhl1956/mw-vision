# MW-Vision Modular Architecture

## Overview

MW-Vision backend has been refactored following the **MindWarehouse paradigm**: modular, independent, reusable components with clear boundaries and manifests.

## Directory Structure

```
backend/
├── core/                  # Core application factory
│   └── app.py            # FastAPI app creation
├── modules/              # Independent modules
│   ├── security/         # Security middleware & metrics
│   │   ├── rate_limiter.py
│   │   ├── security_headers.py
│   │   ├── metrics.py
│   │   └── manifest.json
│   ├── websocket/        # WebSocket management
│   │   ├── manager.py
│   │   ├── handlers.py
│   │   └── manifest.json
│   ├── agents/           # Agent models & state
│   │   ├── models.py
│   │   ├── state.py
│   │   └── manifest.json
│   └── crew/             # Crew state & simulation
│       ├── models.py
│       ├── state.py
│       ├── simulator.py
│       └── manifest.json
├── routers/              # API route handlers
│   ├── main.py
│   ├── agents.py
│   ├── crew.py
│   ├── security.py
│   └── websocket.py
├── main.py              # Original monolithic (deprecated)
└── main_modular.py      # New modular entry point

```

## Module Manifests

Each module has a `manifest.json` declaring:

- **name**: Module identifier
- **version**: Semantic version
- **dependencies**: Required modules/packages
- **exports**: Public API (classes, functions)
- **provides**: Capabilities offered

### Example: Security Module

```json
{
  "name": "security-module",
  "version": "1.0.0",
  "dependencies": ["fastapi", "starlette"],
  "exports": ["RateLimitMiddleware", "SecurityHeadersMiddleware", "SecurityMetrics"],
  "provides": ["rate_limiting", "security_headers", "metrics_tracking"]
}
```

## Dependency Graph

```
core.app
  └─ modules.security (RateLimitMiddleware, SecurityHeadersMiddleware)
  └─ modules.crew (simulate_agent_updates)

routers.websocket
  └─ modules.websocket (manager, handle_message)
      └─ modules.agents (agents, AgentStatus)
      └─ modules.crew (crew_state)
      └─ modules.security (security_metrics)

routers.agents
  └─ modules.agents (agents)
  └─ modules.crew (crew_state)
```

## Benefits

1. **Separation of Concerns**: Each module has a single responsibility
2. **Testability**: Modules can be tested independently
3. **Reusability**: Security, WebSocket modules can be used in other projects
4. **Maintainability**: Clear boundaries reduce coupling
5. **Scalability**: Easy to add new modules without touching existing code

## Migration Guide

### Old (Monolithic)
```python
# main.py - everything in one file (502 lines)
```

### New (Modular)
```python
# main_modular.py
from core.app import create_app
from routers import main_router, agents_router, crew_router

app = create_app()
app.include_router(main_router)
app.include_router(agents_router)
app.include_router(crew_router)
```

## Running the Application

### Development
```bash
uvicorn main_modular:app --host 0.0.0.0 --port 8000 --reload
```

### Production
```bash
uvicorn main_modular:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing

Each module can be tested independently:

```python
# Test security module
from modules.security import SecurityMetrics

metrics = SecurityMetrics()
metrics.increment("threats_detected")
assert metrics.get_all()["threats_detected"] == 1
```

## Future Enhancements

1. **Database Module**: Replace in-memory state with persistent storage
2. **Auth Module**: Add authentication/authorization
3. **Logging Module**: Centralized logging with structured logs
4. **Config Module**: Environment-based configuration
5. **Metrics Module**: Prometheus/Grafana integration
