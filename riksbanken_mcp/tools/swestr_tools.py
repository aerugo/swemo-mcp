"""
Tools for working with the Riksbank's SWESTR data.
"""
from typing import Dict, List, Any, Optional
from datetime import date
from riksbanken_mcp.services.swestr_api import swestr_request
from riksbanken_mcp.models import Observation, InterestRateData

async def fetch_interest_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[Observation]:
    """
    Fetch SWESTR interest rate data from the Riksbank API.
    
    Retrieves SWESTR (Swedish krona Short Term Rate) data for the specified date range.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        List[Observation]: A list of SWESTR rate observations with dates and values
        
    Example:
        >>> from datetime import date
        >>> start_date = date(2022, 1, 1)
        >>> end_date = date(2022, 12, 31)
        >>> rates = await fetch_interest_rate(start_date, end_date)
    """
    params = {}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swestr_request("rates", params)
    raw_rates = response.get("rates", [])
    
    return [Observation(
        date=rate.get("date", rate.get("dt", "")),
        value=float(rate.get("value", rate.get("val", 0.0)))
    ) for rate in raw_rates]

async def get_swestr(from_date: Optional[date] = None, to_date: Optional[date] = None) -> InterestRateData:
    """
    Get SWESTR interest rate data for a specified period.
    
    Retrieves the Swedish krona Short Term Rate (SWESTR) which is the
    Riksbank's transaction-based reference rate.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        InterestRateData: A validated model containing SWESTR rate observations
        
    Example:
        >>> from datetime import date, timedelta
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(days=30)
        >>> swestr_data = await get_swestr(start_date, end_date)
        >>> for rate in swestr_data.observations:
        >>>     print(f"{rate.date}: {rate.value}%")
    """
    observations = await fetch_interest_rate(from_date, to_date)
    return InterestRateData(observations=observations)

async def get_latest_swestr() -> Observation:
    """
    Get the latest published SWESTR interest rate.
    
    Retrieves the most recently published SWESTR rate from the Riksbank.
    
    Returns:
        Observation: The latest SWESTR rate with date and value
        
    Example:
        >>> latest = await get_latest_swestr()
        >>> print(f"Latest SWESTR rate ({latest.date}): {latest.value}%")
    """
    response = await swestr_request("latest")
    rate_data = response.get("rate", {})
    
    return Observation(
        date=rate_data.get("date", rate_data.get("dt", "")),
        value=float(rate_data.get("value", rate_data.get("val", 0.0)))
    )

async def get_swestr_averages(from_date: Optional[date] = None, to_date: Optional[date] = None) -> InterestRateData:
    """
    Get SWESTR average rates.
    
    Retrieves the compounded average rates based on SWESTR.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        InterestRateData: A validated model containing SWESTR average rate observations
    """
    params = {}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swestr_request("averages", params)
    raw_rates = response.get("averages", [])
    
    observations = [Observation(
        date=rate.get("date", rate.get("dt", "")),
        value=float(rate.get("value", rate.get("val", 0.0)))
    ) for rate in raw_rates]
    
    return InterestRateData(observations=observations)

async def get_swestr_1week(from_date: Optional[date] = None, to_date: Optional[date] = None) -> InterestRateData:
    """
    Get 1-week SWESTR average rates.
    
    Retrieves the 1-week compounded average rates based on SWESTR.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        InterestRateData: A validated model containing 1-week SWESTR average rate observations
    """
    params = {"period": "1week"}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swestr_request("averages", params)
    raw_rates = response.get("averages", [])
    
    observations = [Observation(
        date=rate.get("date", rate.get("dt", "")),
        value=float(rate.get("value", rate.get("val", 0.0)))
    ) for rate in raw_rates]
    
    return InterestRateData(observations=observations)

async def get_swestr_1month(from_date: Optional[date] = None, to_date: Optional[date] = None) -> InterestRateData:
    """
    Get 1-month SWESTR average rates.
    
    Retrieves the 1-month compounded average rates based on SWESTR.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        InterestRateData: A validated model containing 1-month SWESTR average rate observations
    """
    params = {"period": "1month"}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swestr_request("averages", params)
    raw_rates = response.get("averages", [])
    
    observations = [Observation(
        date=rate.get("date", rate.get("dt", "")),
        value=float(rate.get("value", rate.get("val", 0.0)))
    ) for rate in raw_rates]
    
    return InterestRateData(observations=observations)
