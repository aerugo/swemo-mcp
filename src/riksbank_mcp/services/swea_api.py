"""
SWEA API helper functions for interacting with the Riksbank's SWEA API.
"""

from typing import Any

import httpx


async def swea_request(
    endpoint: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Make a request to the Riksbank SWEA API.

    Args:
        endpoint: The API endpoint to call
        params: Optional query parameters

    Returns:
        The JSON response from the API
    """
    base_url = "https://api.riksbank.se/swea/v1"
    url = f"{base_url}/{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
