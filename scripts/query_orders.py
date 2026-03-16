"""Query order list (avoids PowerShell encoding issues)."""
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
API_KEY = os.getenv("API_KEY", "")


def main():
    if not API_KEY:
        print("Error: Set API_KEY in .env")
        return 1

    url = f"{API_URL.rstrip('/')}/orders"
    headers = {"X-API-KEY": API_KEY}

    try:
        with httpx.Client() as client:
            resp = client.get(url, headers=headers, timeout=10.0)
            resp.raise_for_status()
            orders = resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if not orders:
        print("No orders yet")
        return 0

    print(f"{len(orders)} order(s)\n")
    for o in orders:
        alert = "✓" if o.get("discord_alert_sent") else " "
        print(f"  {o['order_id']}  ${o['amount']:>10,.0f}  {o['customer_name']}  [{alert}]")
    return 0


if __name__ == "__main__":
    exit(main())
