"""Order query API routes."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_api_key
from app.db.database import get_db
from app.db.order_repository import get_order_by_order_id
from app.models.order import Order

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_class=JSONResponse)
async def list_orders(
    limit: int = 50,
    _: str = Depends(verify_api_key),
    session: AsyncSession = Depends(get_db),
) -> list[dict]:
    """List orders, newest first."""
    result = await session.execute(
        select(Order).order_by(Order.created_at.desc()).limit(limit)
    )
    orders = result.scalars().all()
    data = [
        {
            "order_id": o.order_id,
            "amount": o.amount,
            "customer_name": o.customer_name,
            "discord_alert_sent": o.discord_alert_sent,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]
    return JSONResponse(
        content=data,
        media_type="application/json; charset=utf-8",
    )


@router.get("/{order_id}", response_class=JSONResponse)
async def get_order(
    order_id: str,
    _: str = Depends(verify_api_key),
    session: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Get single order by order_id."""
    order = await get_order_by_order_id(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    data = {
        "order_id": order.order_id,
        "amount": order.amount,
        "customer_name": order.customer_name,
        "discord_alert_sent": order.discord_alert_sent,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }
    return JSONResponse(
        content=data,
        media_type="application/json; charset=utf-8",
    )
