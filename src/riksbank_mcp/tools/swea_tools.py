"""
Tools for working with the Riksbank's SWEA data.
"""

from datetime import date

from pydantic import BaseModel, Field

from riksbank_mcp.models import (
    CalendarDay,
    CrossRate,
    CrossRateAggregate,
    ExchangeRateData,
    InterestRateData,
    Observation,
)
from riksbank_mcp.services.swea_api import swea_request


async def fetch_observations(
    series_id: str, from_date: date | None = None, to_date: date | None = None
) -> list[Observation]:
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

    return [
        Observation(
            date=obs.get("date", obs.get("dt", "")),
            value=float(obs.get("value", obs.get("val", 0.0))),
        )
        for obs in raw_observations
    ]


async def get_policy_rate(
    from_date: date | None = None, to_date: date | None = None
) -> InterestRateData:
    """
    Fetch the official Swedish policy (repo) rate time series.

    The policy rate, set by the Riksbank, influences borrowing costs and liquidity conditions
    in the economy. It is a closely watched indicator by economists and financial professionals.

    Args:
        from_date (Optional[date]): Start of the data range (YYYY-MM-DD).
        to_date (Optional[date]): End of the data range; if None, the latest data is fetched.

    Returns:
        InterestRateData: A model containing a list of interest rate observations.

    Usage Example:
        >>> from datetime import date
        >>> rates = await get_policy_rate(date(2020, 1, 1))
        >>> print("Earliest observation:", rates.observations[0])

    Frequency & Interpretation:
        - Typically updated following policy meetings (every 6-8 weeks).
        - Analysts compare these rates with inflation and GDP forecasts.

    Disclaimer:
        Past rate decisions are not guarantees of future moves; unexpected events may prompt rapid changes.
    """
    observations = await fetch_observations("POLICY_RATE", from_date, to_date)
    return InterestRateData(observations=observations)


async def get_usd_exchange_rate(
    from_date: date | None = None, to_date: date | None = None
) -> ExchangeRateData:
    """
    Retrieve daily or monthly USD/SEK exchange rate data.

    This series helps monitor external competitiveness and the impact of import costs on inflation.

    Args:
        from_date (Optional[date]): Start date for the query.
        to_date (Optional[date]): End date for the query; if omitted, the latest data is returned.

    Returns:
        ExchangeRateData: A model containing USD/SEK observations.

    Usage Example:
        >>> usd_data = await get_usd_exchange_rate()
        >>> for obs in usd_data.observations[-5:]:
        ...     print(f"{obs.date}: {obs.value} SEK per USD")

    Frequency & Range:
        - Typically updated daily on banking days.

    Disclaimer:
        Exchange rate forecasts are uncertain; scenario analyses are recommended for robust planning.
    """
    observations = await fetch_observations("USD_SEK", from_date, to_date)
    return ExchangeRateData(series_id="USD_SEK", observations=observations)


async def get_eur_exchange_rate(
    from_date: date | None = None, to_date: date | None = None
) -> ExchangeRateData:
    """
    Retrieve daily or monthly EUR/SEK exchange rate data.

    This series is critical for Sweden's trade relations with the Eurozone.

    Args:
        from_date (Optional[date]): Start of the data range.
        to_date (Optional[date]): End of the data range.

    Returns:
        ExchangeRateData: A model containing EUR/SEK observations.

    Usage Example:
        >>> eur_data = await get_eur_exchange_rate()
        >>> print("Most recent:", eur_data.observations[-1])

    Disclaimer:
        Macro events can significantly impact this rate; it is advisable to compare with USD/SEK data.
    """
    observations = await fetch_observations("EUR_SEK", from_date, to_date)
    return ExchangeRateData(series_id="EUR_SEK", observations=observations)


async def get_gbp_exchange_rate(
    from_date: date | None = None, to_date: date | None = None
) -> ExchangeRateData:
    """
    Retrieve GBP/SEK exchange rate data.

    This series reflects the exchange rate relevant for trade with the UK.

    Args:
        from_date (Optional[date]): Start date.
        to_date (Optional[date]): End date, or None for the latest data.

    Returns:
        ExchangeRateData: A model containing GBP/SEK observations.

    Usage Example:
        >>> gbp_data = await get_gbp_exchange_rate()
        >>> print("Latest GBP rate:", gbp_data.observations[-1].value, "SEK per GBP")

    Disclaimer:
        Rapid changes in political or economic conditions (e.g. Brexit) can cause sharp fluctuations.
    """
    observations = await fetch_observations("GBP_SEK", from_date, to_date)
    return ExchangeRateData(series_id="GBP_SEK", observations=observations)


async def get_mortgage_rate(
    from_date: date | None = None, to_date: date | None = None
) -> InterestRateData:
    """
    Retrieve average mortgage interest rate data in Sweden.

    This series reflects lending costs for home loans and influences consumption and housing demand.

    Args:
        from_date (Optional[date]): Earliest date to include.
        to_date (Optional[date]): Latest date to include.

    Returns:
        InterestRateData: A model containing mortgage rate observations.

    Usage Example:
        >>> from datetime import date
        >>> mortgage_rates = await get_mortgage_rate(date(2019, 1, 1))
        >>> print("Data points:", len(mortgage_rates.observations))

    Disclaimer:
        This average does not capture regional variations or distinctions between fixed and variable rates.
    """
    observations = await fetch_observations("MORTGAGE_RATE", from_date, to_date)
    return InterestRateData(observations=observations)


async def get_calendar_days(
    from_date: date,
    to_date: date | None = None
) -> list[CalendarDay]:
    """
    Retrieve calendar days information from the SWEA API.
    
    Args:
        from_date: Start date for the query
        to_date: Optional end date for the query
        
    Returns:
        List of CalendarDay objects
    """
    endpoint = f"CalendarDays/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"
    response = await swea_request(endpoint)
    if not response:
        return []
    return [CalendarDay(**item) for item in response]


async def get_cross_rates(
    series_id1: str,
    series_id2: str,
    from_date: date,
    to_date: date | None = None
) -> list[CrossRate]:
    """
    Retrieve cross rates between two currency series.
    
    Args:
        series_id1: First currency series ID
        series_id2: Second currency series ID
        from_date: Start date for the query
        to_date: Optional end date for the query
        
    Returns:
        List of CrossRate objects
    """
    endpoint = f"CrossRates/{series_id1}/{series_id2}/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"
    response = await swea_request(endpoint)
    if not response:
        return []
    return [CrossRate(**item) for item in response]


async def get_cross_rate_aggregates(
    series_id1: str,
    series_id2: str,
    aggregation: str,
    from_date: date,
    to_date: date | None = None
) -> list[CrossRateAggregate]:
    """
    Retrieve aggregated cross rates between two currency series.
    
    Args:
        series_id1: First currency series ID
        series_id2: Second currency series ID
        aggregation: Aggregation type (e.g., 'Monthly', 'Quarterly', 'Yearly')
        from_date: Start date for the query
        to_date: Optional end date for the query
        
    Returns:
        List of CrossRateAggregate objects
    """
    endpoint = f"CrossRateAggregates/{series_id1}/{series_id2}/{aggregation}/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"
    response = await swea_request(endpoint)
    if not response:
        return []
    return [CrossRateAggregate(**item) for item in response]


class ObservationAggregate(BaseModel):
    """
    Represents an aggregated observation (e.g. monthly, quarterly),
    as returned by the SWEA API /ObservationAggregates endpoints.
    """
    year: int
    seqNr: int
    from_: str = Field(..., alias="from")
    to: str
    average: float
    min: float
    max: float
    ultimo: float
    observationCount: int


async def get_observation_aggregates(
    series_id: str,
    aggregation: str,
    from_date: date,
    to_date: date | None = None
) -> list[ObservationAggregate]:
    """
    Retrieve aggregated observations for a specific series.
    
    Args:
        series_id: The series ID to query
        aggregation: Aggregation type (e.g., 'Monthly', 'Quarterly', 'Yearly')
        from_date: Start date for the query
        to_date: Optional end date for the query
        
    Returns:
        List of ObservationAggregate objects
    """
    endpoint = f"ObservationAggregates/{series_id}/{aggregation}/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"
    response = await swea_request(endpoint)
    if not response:
        return []
    return [ObservationAggregate(**item) for item in response]


async def get_latest_observation(series_id: str) -> Observation | None:
    """
    Retrieve the latest observation for a specific series.
    
    Args:
        series_id: The series ID to query
        
    Returns:
        An Observation object or None if no data is available
    """
    endpoint = f"Observations/Latest/{series_id}"
    response = await swea_request(endpoint)
    if not response:
        return None
    return Observation(
        date=response.get("date", ""),
        value=float(response.get("value", 0.0))
    )


async def list_groups(language: str = "en") -> dict:
    """
    List all available groups in the SWEA API.
    
    Args:
        language: Language code for the response (default: "en")
        
    Returns:
        Dictionary containing group information
    """
    params = {"language": language}
    response = await swea_request("groups", params)
    return response or {}


async def get_group_details(group_id: int, language: str = "en") -> dict:
    """
    Get details for a specific group.
    
    Args:
        group_id: The ID of the group to query
        language: Language code for the response (default: "en")
        
    Returns:
        Dictionary containing group details
    """
    endpoint = f"Groups/{group_id}"
    params = {"language": language}
    response = await swea_request(endpoint, params)
    return response or {}


async def list_series(language: str = "en") -> list:
    """
    List all available series in the SWEA API.
    
    Args:
        language: Language code for the response (default: "en")
        
    Returns:
        List of series information
    """
    params = {"language": language}
    response = await swea_request("series", params)
    if not response:
        return []
    return response


async def get_series_info(series_id: str, language: str = "en") -> dict | None:
    """
    Get information about a specific series.
    
    Args:
        series_id: The ID of the series to query
        language: Language code for the response (default: "en")
        
    Returns:
        Dictionary containing series information or None if not found
    """
    endpoint = f"Series/{series_id}"
    params = {"language": language}
    response = await swea_request(endpoint, params)
    return response if response else None


async def list_exchange_rate_series(language: str = "en") -> list:
    """
    List all available exchange rate series in the SWEA API.
    
    Args:
        language: Language code for the response (default: "en")
        
    Returns:
        List of exchange rate series information
    """
    endpoint = "Series/ExchangeRateSeries"
    params = {"language": language}
    response = await swea_request(endpoint, params)
    if not response:
        return []
    return response
