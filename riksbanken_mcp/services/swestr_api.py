"""
SWESTR API helper functions for interacting with the Riksbank's SWESTR API.
"""
import httpx
from typing import Dict, Any, Optional

async def swestr_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Make a request to the Riksbank SWESTR API.
    
    Args:
        endpoint: The API endpoint to call
        params: Optional query parameters
        
    Returns:
        The JSON response from the API
    """
    base_url = "https://api.riksbank.se/swestr/api/v1"
    url = f"{base_url}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
