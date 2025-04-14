"""
Monetary Policy API helper functions for interacting with the Riksbank's Monetary Policy API.
"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from riksbank_mcp.openapi import MONETARY_POLICY_SPEC

# Set up logging
logger = logging.getLogger(__name__)

# Extract base URL from the OpenAPI spec
BASE_URL = MONETARY_POLICY_SPEC["servers"][0]["url"]

async def riksbanken_request(
    endpoint: str, params: Optional[Dict[str, Any]] = None, retries: int = 5
) -> Dict[str, Any]:
    """
    Make a request to the Riksbank Monetary Policy API with automatic retries for 429 errors.

    Args:
        endpoint: The API endpoint to call
        params: Optional query parameters
        retries: Number of retries on a 429 error. Default is 5.

    Returns:
        The JSON response from the API
        
    Raises:
        HTTPStatusError if the request fails after all retries
    """
    url = f"{BASE_URL}/{endpoint}"

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                logger.debug(f"Making request to {url} with params {params}")
                response = await client.get(url, params=params)
                response.raise_for_status()
                # Only try to decode JSON if we have content
                if response.content:
                    return response.json()
                return {}
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    logger.warning(f"Got 404 at {url}, returning empty response.")
                    return {}
                if response.status_code == 429 and attempt < retries - 1:
                    # Wait with exponential backoff
                    wait_seconds = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                    logger.warning(f"Rate limited (429). Retrying in {wait_seconds} second(s)...")
                    await asyncio.sleep(wait_seconds)
                    continue
                else:
                    logger.error(f"Request failed after {attempt+1} attempts for endpoint: {endpoint}")
                    raise
        raise Exception(f"Max retries exceeded for URL: {url}")
