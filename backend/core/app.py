"""
FastAPI Application Factory
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.security import RateLimitMiddleware, SecurityHeadersMiddleware
from modules.crew import simulate_agent_updates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background simulation task."""
    task = asyncio.create_task(simulate_agent_updates())
    yield
    task.cancel()


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="MW-Vision Backend",
        description="Secure WebSocket backend for MW-Vision Visual Command Center",
        version="3.0.0",
        lifespan=lifespan
    )

    # Add security middleware
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    app.add_middleware(SecurityHeadersMiddleware)

    # Restricted CORS (only localhost for development)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5189", "http://127.0.0.1:5189"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    return app
