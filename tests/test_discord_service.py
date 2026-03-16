"""Discord service logic tests."""
import pytest
from unittest.mock import AsyncMock, patch

from app.schemas.order import OrderIn
from app.services.discord_service import send_high_value_alert


@pytest.mark.asyncio
async def test_send_alert_skipped_when_below_threshold():
    """No send when amount below threshold."""
    order = OrderIn(order_id="ORD-001", amount=500, customer_name="Alice")
    with patch("app.services.discord_service.httpx.AsyncClient") as mock_client:
        result = await send_high_value_alert(order)
        assert result is False
        mock_client.return_value.__aenter__.return_value.post.assert_not_called()


@pytest.mark.asyncio
async def test_send_alert_called_when_above_threshold():
    """Send when amount above threshold."""
    order = OrderIn(order_id="ORD-001", amount=1500, customer_name="Alice")
    mock_response = AsyncMock()
    mock_response.is_success = True
    with patch("app.services.discord_service.httpx.AsyncClient") as mock_client:
        mock_post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.post = mock_post
        result = await send_high_value_alert(order)
        assert result is True
        mock_post.assert_called_once()
