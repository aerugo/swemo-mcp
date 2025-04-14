"""
Monetary Policy API helper functions for interacting with the Riksbank's Monetary Policy API.
"""

from typing import Any

import httpx


async def riksbanken_request(
    endpoint: str, params: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Make a request to the Riksbank Monetary Policy API.

    Args:
        endpoint: The API endpoint to call
        params: Optional query parameters

    Returns:
        The JSON response from the API
    """
    base_url = "https://api.riksbank.se/monetary_policy_data/v1"
    url = f"{base_url}/{endpoint}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
