"""
SWESTR API helper functions for interacting with the Riksbank's SWESTR API.
"""

from typing import Any
import asyncio

import httpx


async def swestr_request(
    endpoint: str, params: dict[str, Any] | None = None, retries: int = 5
) -> dict[str, Any]:
    """
    Make a request to the Riksbank SWESTR API with automatic retries for 429 errors.

    Args:
        endpoint: The API endpoint to call
        params: Optional query parameters
        retries: Number of retries on a 429 error. Default is 5.

    Returns:
        The JSON response from the API
        
    Raises:
        HTTPStatusError if the request fails after all retries
    """
    base_url = "https://api.riksbank.se/swestr/v1"
    url = f"{base_url}/{endpoint}"

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                # Only try to decode JSON if we have content
                if response.content:
                    return response.json()
                return {}
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    # No data available for the specified period
                    return {}
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
