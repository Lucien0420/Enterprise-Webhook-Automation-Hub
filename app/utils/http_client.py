"""Shared HTTP client for connection pooling."""
import httpx

http_client: httpx.AsyncClient | None = None


def get_http_client() -> httpx.AsyncClient:
    """Get shared async HTTP client."""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=30.0)
    return http_client


async def close_http_client() -> None:
    """Close HTTP client, release connections."""
    global http_client
    if http_client is not None:
        await http_client.aclose()
        http_client = None
