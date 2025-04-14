"""
Tools for working with the Riksbank's SWEA data.
"""
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from riksbanken_mcp.services.swea_api import swea_request
from riksbanken_mcp.models import Observation, ExchangeRateData, InterestRateData

async def fetch_observations(series_id: str, from_date: Optional[date] = None, to_date: Optional[date] = None) -> List[Observation]:
    """
    Fetch observations for a specific series from the SWEA API.
    
    Retrieves time series data for the specified series ID within the given date range.
    
    Args:
        series_id (str): The ID of the series to fetch
        from_date (Optional[date]): Optional start date for the data
        to_date (Optional[date]): Optional end date for the data
        
    Returns:
        List[Observation]: A list of observations with dates and values
        
    Example:
        >>> from datetime import date
        >>> start_date = date(2022, 1, 1)
        >>> end_date = date(2022, 12, 31)
        >>> observations = await fetch_observations("POLICY_RATE", start_date, end_date)
    """
    params = {"seriesid": series_id}
    
    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()
        
    response = await swea_request("observations", params)
    raw_observations = response.get("observations", [])
    
    return [Observation(
        date=obs.get("date", obs.get("dt", "")),
        value=float(obs.get("value", obs.get("val", 0.0)))
    ) for obs in raw_observations]

async def get_policy_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> InterestRateData:
    """
    Get the Riksbank's policy rate data.
    
    Retrieves the official policy interest rate (repo rate) set by the Swedish central bank.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        InterestRateData: A validated model containing policy rate observations
        
    Example:
        >>> from datetime import date
        >>> start = date(2020, 1, 1)
        >>> end = date(2023, 12, 31)
        >>> policy_rates = await get_policy_rate(start, end)
        >>> for rate in policy_rates.observations:
        >>>     print(f"{rate.date}: {rate.value}%")
    """
    observations = await fetch_observations("POLICY_RATE", from_date, to_date)
    return InterestRateData(observations=observations)

async def get_usd_exchange_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> ExchangeRateData:
    """
    Get USD/SEK exchange rate data.
    
    Retrieves the exchange rate between US Dollar and Swedish Krona.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        ExchangeRateData: A validated model containing exchange rate observations
        
    Example:
        >>> from datetime import date, timedelta
        >>> end_date = date.today()
        >>> start_date = end_date - timedelta(days=30)
        >>> usd_rates = await get_usd_exchange_rate(start_date, end_date)
        >>> latest = usd_rates.observations[-1] if usd_rates.observations else None
        >>> if latest:
        >>>     print(f"Latest USD/SEK rate: {latest.value}")
    """
    observations = await fetch_observations("USD_SEK", from_date, to_date)
    return ExchangeRateData(
        series_id="USD_SEK",
        observations=observations
    )

async def get_eur_exchange_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> ExchangeRateData:
    """
    Get EUR/SEK exchange rate data.
    
    Retrieves the exchange rate between Euro and Swedish Krona.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        ExchangeRateData: A validated model containing exchange rate observations
    """
    observations = await fetch_observations("EUR_SEK", from_date, to_date)
    return ExchangeRateData(
        series_id="EUR_SEK",
        observations=observations
    )

async def get_gbp_exchange_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> ExchangeRateData:
    """
    Get GBP/SEK exchange rate data.
    
    Retrieves the exchange rate between British Pound and Swedish Krona.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        ExchangeRateData: A validated model containing exchange rate observations
    """
    observations = await fetch_observations("GBP_SEK", from_date, to_date)
    return ExchangeRateData(
        series_id="GBP_SEK",
        observations=observations
    )

async def get_mortgage_rate(from_date: Optional[date] = None, to_date: Optional[date] = None) -> InterestRateData:
    """
    Get average mortgage rate data.
    
    Retrieves the average mortgage interest rate in Sweden.
    
    Args:
        from_date (Optional[date]): Optional start date for the data range
        to_date (Optional[date]): Optional end date for the data range
        
    Returns:
        InterestRateData: A validated model containing mortgage rate observations
    """
    observations = await fetch_observations("MORTGAGE_RATE", from_date, to_date)
    return InterestRateData(observations=observations)
