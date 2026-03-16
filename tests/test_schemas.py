"""OrderIn schema validation tests."""
import pytest
from pydantic import ValidationError

from app.schemas.order import OrderIn


def test_order_in_valid():
    """Valid order passes validation."""
    order = OrderIn(order_id="ORD-001", amount=100.0, customer_name="Alice")
    assert order.order_id == "ORD-001"
    assert order.amount == 100.0
    assert order.customer_name == "Alice"


def test_order_in_amount_must_be_positive():
    """Amount must be > 0."""
    with pytest.raises(ValidationError):
        OrderIn(order_id="ORD-001", amount=0, customer_name="Alice")
    with pytest.raises(ValidationError):
        OrderIn(order_id="ORD-001", amount=-100, customer_name="Alice")
