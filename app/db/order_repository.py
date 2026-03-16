"""Order data access."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderIn


async def get_order_by_order_id(session: AsyncSession, order_id: str) -> Order | None:
    """Find order by order_id (for idempotency check)."""
    result = await session.execute(select(Order).where(Order.order_id == order_id))
    return result.scalars().first()


async def create_order(
    session: AsyncSession,
    order: OrderIn,
    discord_alert_sent: bool = False,
) -> Order:
    """Create order record."""
    db_order = Order(
        order_id=order.order_id,
        amount=order.amount,
        customer_name=order.customer_name,
        discord_alert_sent=discord_alert_sent,
    )
    session.add(db_order)
    await session.flush()
    return db_order
