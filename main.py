"""Enterprise Webhook Automation Hub - entry point."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.order_routes import router as order_router
from app.api.webhook_routes import router as webhook_router
from app.core.limiter import limiter
from app.db.database import init_db

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Enterprise Webhook Automation Hub",
    description="Integration hub: receive orders via webhook, send Discord alerts by rules",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(webhook_router)
app.include_router(order_router)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/")
async def root() -> dict:
    """API info."""
    return {"status": "ok", "docs": "/docs", "demo": "/demo", "health": "/health"}


@app.get("/health")
async def health() -> dict:
    """Health check: DB connectivity."""
    from sqlalchemy import text

    from app.db.database import engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "ok"}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "detail": str(e)}


@app.get("/demo")
async def demo() -> RedirectResponse:
    """Redirect to demo checkout page."""
    return RedirectResponse(url="/static/demo.html")
