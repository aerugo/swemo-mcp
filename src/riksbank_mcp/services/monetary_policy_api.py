"""
Monetary Policy API helper functions for interacting with the Riksbank's Monetary Policy API.
"""

import asyncio
import logging
from typing import Any
from urllib.parse import urlencode

import httpx

# Set up logging
logger = logging.getLogger(__name__)

# Extract base URL from the OpenAPI spec
BASE_URL = "https://api.riksbank.se/monetary_policy_data/v1/forecasts"


async def riksbanken_request(
    endpoint: str = "",
    params: dict[str, Any] | None = None,
    retries: int = 5,
) -> dict[str, Any]:
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
    url = BASE_URL
    if endpoint:
        url = f"{BASE_URL}/{endpoint}"

    params = params or {}
    query_string = urlencode(params, safe=":")
    full_url = f"{url}?{query_string}"

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                logger.debug(f"Requesting: {full_url}")
                response = await client.get(full_url)
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 404:
                    logger.warning(f"Got 404 at {full_url}, returning empty.")
                    return {}
                if status == 429 and attempt < retries - 1:
                    wait = 2**attempt
                    logger.warning(f"Rate limited, retrying in {wait}s…")
                    await asyncio.sleep(wait)
                    continue
                logger.error(f"Failed after {attempt+1} tries: {full_url}")
                raise
        raise RuntimeError(f"Max retries exceeded for {full_url}")
