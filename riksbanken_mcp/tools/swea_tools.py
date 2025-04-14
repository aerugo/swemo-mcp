"""
Tools for working with the Riksbank's SWEA data.
"""
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from riksbanken_mcp.services.swea_api import swea_request

async def fetch_observations(series_id: str, from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Fetch observations for a specific series.
    
    Args:
        series_id: The ID of the series to fetch
        from_date: Optional start date for the data
        to_date: Optional end date for the data
        
    Returns:
        Observation data for the requested series
    """
    params = {"seriesid": series_id}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swea_request("observations", params)
    return response["observations"]

async def get_policy_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Get the Riksbank's policy rate data.
    
    Args:
        from_date: Optional start date
        to_date: Optional end date
        
    Returns:
        Policy rate data
    """
    return await fetch_observations("POLICY_RATE", from_date, to_date)

async def get_usd_exchange_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Get USD/SEK exchange rate data.
    
    Args:
        from_date: Optional start date
        to_date: Optional end date
        
    Returns:
        Exchange rate data
    """
    return await fetch_observations("USD_SEK", from_date, to_date)
