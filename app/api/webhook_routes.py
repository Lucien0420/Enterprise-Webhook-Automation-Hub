"""Webhook API routes."""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_api_key
from app.core.config import settings
from app.core.limiter import limiter
from app.db.database import get_db
from app.db.order_repository import create_order, get_order_by_order_id
from app.schemas.order import OrderIn
from app.services.discord_service import send_high_value_alert

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/order")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def receive_order(
    request: Request,
    order: OrderIn,
    _: str = Depends(verify_api_key),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """
    Receive order webhook.
    Idempotent: same order_id processed once.
    Sends Discord alert when amount exceeds threshold.
    """
    existing = await get_order_by_order_id(session, order.order_id)
    if existing:
        return {
            "status": "received",
            "order_id": order.order_id,
            "discord_alert_sent": existing.discord_alert_sent,
            "duplicate": True,
        }

    discord_sent = await send_high_value_alert(order)
    await create_order(session, order, discord_alert_sent=discord_sent)

    return {
        "status": "received",
        "order_id": order.order_id,
        "discord_alert_sent": discord_sent,
    }
