"""
SWEA API helper functions for interacting with the Riksbank's SWEA API.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx


async def swea_request(
    endpoint: str, params: dict[str, Any] | None = None, retries: int = 5
) -> dict[str, Any]:
    """
    Make a request to the Riksbank SWEA API with automatic retries for 429 errors.
    
    Args:
        endpoint: The API endpoint to call
        params: Optional query parameters
        retries: Number of retries on a 429 error. Default is 5.

    Returns:
        The JSON response from the API
        
    Raises:
        HTTPStatusError if the request fails after all retries
    """
    base_url: str = "https://api.riksbank.se/swea/v1"
    url: str = f"{base_url}/{endpoint}"

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                response: httpx.Response = await client.get(url, params=params)
                response.raise_for_status()
                # Only try to decode JSON if we have content
                if response.content:
                    return response.json()
                return {}
            except httpx.HTTPStatusError as exc:
                if response.status_code == 429 and attempt < retries - 1:
                    # Wait with exponential backoff
                    wait_seconds = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                    print(f"Rate limited (429). Retrying in {wait_seconds} second(s)...")
                    await asyncio.sleep(wait_seconds)
                    continue
                else:
                    print(f"Request failed after {attempt+1} attempts for endpoint: {endpoint}")
                    raise
        raise Exception(f"Max retries exceeded for URL: {url}")
