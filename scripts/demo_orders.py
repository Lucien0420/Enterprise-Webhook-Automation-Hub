"""Batch send sample orders for demo."""
import os
import random
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "")

DEMO_ORDERS = [
    {"order_id": "ORD-DEMO-001", "amount": 850, "customer_name": "Alice Chen"},
    {"order_id": "ORD-DEMO-002", "amount": 2300, "customer_name": "Bob Lin"},
    {"order_id": "ORD-DEMO-003", "amount": 450, "customer_name": "Carol Zhang"},
    {"order_id": "ORD-DEMO-004", "amount": 5800, "customer_name": "David Wang"},
    {"order_id": "ORD-DEMO-005", "amount": 1200, "customer_name": "Eva Li"},
    {"order_id": "ORD-DEMO-006", "amount": 320, "customer_name": "Frank Wu"},
    {"order_id": "ORD-DEMO-007", "amount": 9900, "customer_name": "Grace Huang"},
    {"order_id": "ORD-DEMO-008", "amount": 1500, "customer_name": "Henry Liu"},
]


def send_order(client: httpx.Client, order: dict) -> bool:
    """Send single order."""
    url = f"{API_URL.rstrip('/')}/webhook/order"
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY,
    }
    try:
        resp = client.post(url, json=order, headers=headers, timeout=10.0)
        if resp.is_success:
            data = resp.json()
            if data.get("duplicate"):
                alert = "(duplicate)" + (" - alert was sent" if data.get("discord_alert_sent") else "")
            elif data.get("discord_alert_sent"):
                alert = "✓ Discord alert sent"
            else:
                alert = "(below threshold)"
            print(f"  {order['order_id']} ${order['amount']:,.0f} - {order['customer_name']} {alert}")
            return True
        else:
            print(f"  {order['order_id']} ✗ Failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"  {order['order_id']} ✗ Error: {e}")
        return False


def main():
    if not API_KEY:
        print("Error: Set API_KEY in .env")
        return 1

    print("=" * 50)
    print("Enterprise Webhook Automation Hub - Demo Batch")
    print("=" * 50)
    print(f"Target: {API_URL}")
    print(f"Orders: {len(DEMO_ORDERS)}")
    print("-" * 50)

    orders = DEMO_ORDERS.copy()
    random.shuffle(orders)

    success = 0
    with httpx.Client() as client:
        for i, order in enumerate(orders, 1):
            print(f"[{i}/{len(orders)}]", end=" ")
            if send_order(client, order):
                success += 1
            time.sleep(0.5)

    print("-" * 50)
    print(f"Done: {success}/{len(orders)} succeeded")
    print("Check Discord for alerts (orders with amount > 1000)")
    return 0 if success == len(orders) else 1


if __name__ == "__main__":
    exit(main())
