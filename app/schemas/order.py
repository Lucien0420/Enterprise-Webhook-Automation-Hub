"""Order Pydantic models."""
from pydantic import BaseModel, Field


class OrderIn(BaseModel):
    """Order payload from webhook."""

    order_id: str
    amount: float = Field(..., gt=0, description="Order amount, must be > 0")
    customer_name: str
