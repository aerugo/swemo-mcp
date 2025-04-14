"""
Tools for working with the Riksbank's SWESTR data.
"""
from typing import Dict, List, Any, Optional
from datetime import date
from riksbanken_mcp.services.swestr_api import swestr_request

async def fetch_interest_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Fetch SWESTR interest rate data.
    
    Args:
        from_date: Optional start date for the data
        to_date: Optional end date for the data
        
    Returns:
        SWESTR interest rate data
    """
    params = {}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swestr_request("rates", params)
    return response["rates"]

async def get_swestr(from_date: Optional[date] = None, to_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Get SWESTR interest rate data.
    
    Args:
        from_date: Optional start date
        to_date: Optional end date
        
    Returns:
        SWESTR interest rate data
    """
    return await fetch_interest_rate(from_date, to_date)

async def get_latest_swestr() -> Dict[str, Any]:
    """
    Get the latest SWESTR interest rate.
    
    Returns:
        The latest SWESTR interest rate data
    """
    response = await swestr_request("latest")
    return response["rate"]
