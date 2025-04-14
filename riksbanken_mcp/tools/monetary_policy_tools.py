"""
Tools for working with the Riksbank's Monetary Policy data.
"""
from typing import Dict, List, Any, Optional
from riksbanken_mcp.services.monetary_policy_api import riksbanken_request

async def list_policy_rounds() -> List[Dict[str, Any]]:
    """
    List all available monetary policy rounds.
    
    Returns:
        A list of policy rounds
    """
    response = await riksbanken_request("policy-rounds")
    return response["policyRounds"]

async def list_series_ids() -> List[Dict[str, Any]]:
    """
    List all available series IDs for forecasts.
    
    Returns:
        A list of series IDs and metadata
    """
    response = await riksbanken_request("series")
    return response["series"]

async def get_forecast_data(series_id: str, policy_round: Optional[str] = None) -> Dict[str, Any]:
    """
    Get forecast data for a specific series.
    
    Args:
        series_id: The ID of the series to fetch
        policy_round: Optional policy round ID
        
    Returns:
        Forecast data for the requested series
    """
    params = {"seriesid": series_id}
    if policy_round:
        params["policyround"] = policy_round
        
    response = await riksbanken_request("forecasts", params)
    return response["forecasts"]

async def get_gdp_data(policy_round: Optional[str] = None) -> Dict[str, Any]:
    """
    Get GDP forecast data.
    
    Args:
        policy_round: Optional policy round ID
        
    Returns:
        GDP forecast data
    """
    return await get_forecast_data("GDP", policy_round)
