"""Discord notification service for high-value order alerts."""
import asyncio
import logging

import httpx

from app.core.config import settings
from app.schemas.order import OrderIn

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY_BASE = 1.0


async def send_high_value_alert(order: OrderIn) -> bool:
    """
    Send alert to Discord when order amount exceeds threshold.

    Returns:
        True if sent successfully, False otherwise.
    """
    if order.amount <= settings.alert_threshold:
        return False

    embed = {
        "title": "High-Value Order Alert",
        "color": 0xFF0000,
        "fields": [
            {"name": "Order ID", "value": order.order_id, "inline": True},
            {"name": "Amount", "value": f"${order.amount:,.2f}", "inline": True},
            {"name": "Customer", "value": order.customer_name, "inline": False},
        ],
    }

    payload = {"embeds": [embed]}

    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    settings.discord_webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json; charset=utf-8"},
                )
                if response.is_success:
                    return True
                logger.warning(
                    "Discord webhook failed (attempt %d/%d): status=%s",
                    attempt + 1,
                    MAX_RETRIES,
                    response.status_code,
                )
            except Exception as e:
                logger.warning(
                    "Discord webhook error (attempt %d/%d): %s",
                    attempt + 1,
                    MAX_RETRIES,
                    e,
                )
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY_BASE * (2**attempt)
                await asyncio.sleep(delay)
        return False
