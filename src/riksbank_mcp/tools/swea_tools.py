"""
Tools for working with the Riksbank's SWEA data.
"""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

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


class ObservationAggregate(BaseModel):
    """
    Represents an aggregated observation (e.g. weekly, monthly, quarterly, yearly)
    as returned by the SWEA API /ObservationAggregates endpoints.

    Fields:
        year (int): Calendar or fiscal year of this aggregate.
        seq_nr (int): Sequence index of the aggregate within the year (e.g., which week/quarter).
        from_date (str): Start date of the aggregated period, ISO 8601 (YYYY-MM-DD).
        to_date (str): End date of the aggregated period, ISO 8601 (YYYY-MM-DD).
        average (float): Average value across all underlying observations in the period.
        min (float): Minimum observed value in the period.
        max (float): Maximum observed value in the period.
        ultimo (float): The last valid observation in the period (e.g., last bank day).
        observation_count (int): Number of actual daily observations included in the aggregate.

    Usage:
        Use `get_observation_aggregates` for retrieving aggregated results directly from the SWEA API.
        Analysts can use these aggregates to monitor monthly, quarterly, or yearly trends in interest rates
        or exchange rates without manually summarizing daily observations.
    """

    year: int = Field(..., alias="year")
    seq_nr: int = Field(..., alias="seqNr")
    from_date: str = Field(..., alias="from")
    to_date: str = Field(..., alias="to")
    average: float
    min: float
    max: float
    ultimo: float
    observation_count: int = Field(..., alias="observationCount")

    class Config:
        allow_population_by_field_name = True


async def fetch_observations(
    series_id: str, from_date: date, to_date: Optional[date] = None
) -> list[Observation]:
    """
    Fetch daily observations for a specific series from the SWEA API.

    Each returned observation includes:
      - date (YYYY-MM-DD)
      - value (float)

    This low-level utility typically powers other domain-specific functions.

    Args:
        series_id (str): The series identifier (e.g., "SEKUSPMI" for USD/SEK).
        from_date (date): Start date for the query (required).
        to_date (Optional[date]): End date; if omitted, fetches from `from_date` to the latest available data.

    Returns:
        list[Observation]: A time series of observations with date and value.

    Warnings:
        - If no data exists in the specified interval, returns an empty list.
        - Observations are subject to Riksbank disclaimers, e.g. usage only for informational purposes.

    Usage Example:
        >>> from datetime import date
        >>> start_date = date(2023, 1, 1)
        >>> end_date = date(2023, 6, 1)
        >>> obs = await fetch_observations("SEKUSDPMP", start_date, end_date)
        >>> for o in obs[:5]:
        ...     print(o.date, o.value)
    """
    endpoint = f"Observations/{series_id}/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"

    response = await swea_request(endpoint)
    if not response:
        return []

    return [Observation.model_validate(item) for item in response]


async def get_observation_aggregates(
    series_id: str, aggregation: str, from_date: date, to_date: Optional[date] = None
) -> list[ObservationAggregate]:
    """
    Retrieve aggregated observations (e.g. weekly, monthly, quarterly, yearly) for a given series.

    The Riksbank’s SWEA API can directly compute aggregates:
      - W: weekly
      - M: monthly
      - Q: quarterly
      - Y: yearly

    Each aggregate object includes fields like `average`, `min`, `max`, `ultimo`, and the observation count.

    Args:
        series_id (str): The SWEA series identifier.
        aggregation (str): One of ["W", "M", "Q", "Y"].
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date for the query; if omitted, fetches until most recent date.

    Returns:
        list[ObservationAggregate]: A series of aggregated data points.

    Example:
        >>> # Retrieve monthly aggregates of the policy rate from 2022 onwards
        >>> from datetime import date
        >>> monthly_data = await get_observation_aggregates("SE0001", "M", date(2022, 1, 1))
        >>> print(monthly_data[0])
        ObservationAggregate(
            year=2022, seq_nr=1, from_date='2022-01-01', to_date='2022-01-31',
            average=0.25, min=0.25, max=0.25, ultimo=0.25, observation_count=31
        )

    Note:
        - The Riksbank may limit the returned dataset to 1 year if W or M is used, unless Q or Y is chosen.
        - For large-scale or multiple-year analysis, be sure to partition queries or switch to Q/Y aggregates.
    """
    endpoint = (
        f"ObservationAggregates/{series_id}/{aggregation}/{from_date.isoformat()}"
    )
    if to_date:
        endpoint += f"/{to_date.isoformat()}"

    response = await swea_request(endpoint)
    if not response:
        return []

    return [ObservationAggregate.model_validate(item) for item in response]


async def get_latest_observation(series_id: str) -> Observation | None:
    """
    Retrieve the latest single observation for a specific series.

    In many macroeconomic or financial contexts, only the most recent data point is needed to gauge
    the current state of the market or policy. For instance, the latest policy rate or exchange rate.

    Args:
        series_id (str): The SWEA series identifier.

    Returns:
        Observation or None: The observation object (date, value) for the latest available date, or None if no data.

    Example:
        >>> latest_policy_rate = await get_latest_observation("SE0001")
        >>> print(latest_policy_rate.date, latest_policy_rate.value)

    Disclaimer:
        - Verify data recency, especially if the Riksbank hasn’t published data yet for the current day.
        - This method is ideal for dashboards or quick market checks.
    """
    endpoint = f"Observations/Latest/{series_id}"
    response = await swea_request(endpoint)
    if not response:
        return None
    return Observation.model_validate(response)


async def get_policy_rate(
    from_date: date, to_date: Optional[date] = None
) -> InterestRateData:
    """
    Fetch the Swedish Policy (Repo) Rate time series from the Riksbank.

    This official rate influences broader market rates and is key to monetary policy.
    Series ID used here is an internal code referencing the policy rate in the new API.

    Args:
        from_date (date): Start date (YYYY-MM-DD).
        to_date (Optional[date]): End date or None for latest.

    Returns:
        InterestRateData: A typed model containing a list of daily observations.

    Example:
        >>> from datetime import date
        >>> rates = await get_policy_rate(date(2023, 1, 1))
        >>> for r in rates.observations:
        ...     print(r.date, r.value)

    Usage:
        - Analysis of monetary policy impact
        - Charting rate changes over time
        - Combining with inflation or GDP data to see macro correlations

    Warning:
        - Data is public, but always cite "Source: Sveriges riksbank".
        - Past decisions do not predict future rate moves.
    """
    # NOTE: Replace "SE0001" with the actual series ID for the policy rate in the new REST API if needed.
    policy_rate_series_id = "SE0001"
    observations = await fetch_observations(policy_rate_series_id, from_date, to_date)
    return InterestRateData(observations=observations)


async def get_usd_exchange_rate(
    from_date: date, to_date: Optional[date] = None
) -> ExchangeRateData:
    """
    Retrieve the USD/SEK exchange rate time series from the SWEA API.

    Understanding the USD/SEK rate is vital for:
      - International trade analysis
      - Inflation pass-through from imported goods
      - Market risk assessments

    Args:
        from_date (date): Start date of the data range.
        to_date (Optional[date]): End date; if None, fetches up to the latest publication.

    Returns:
        ExchangeRateData: Contains series_id='USD_SEK' and a list of daily observations.

    Usage Example:
        >>> from datetime import date
        >>> data = await get_usd_exchange_rate(date(2023, 1, 1))
        >>> for obs in data.observations[:5]:
        ...     print(obs.date, obs.value)

    Note:
        - The naming "USD_SEK" is for illustration. Replace with actual ID if the Riksbank uses a different code.
        - To invert the rate for SEK/USD, compute 1 / value or use the SEKETT approach.
    """
    # Example series ID; adapt as needed to match the new system's ID for USD/SEK
    usd_series_id = "SEKUSDPMI"  # or "USDSEKPMI"
    observations = await fetch_observations(usd_series_id, from_date, to_date)
    return ExchangeRateData(series_id=usd_series_id, observations=observations)


async def get_eur_exchange_rate(
    from_date: date, to_date: Optional[date] = None
) -> ExchangeRateData:
    """
    Retrieve the EUR/SEK exchange rate time series from the SWEA API.

    The Eurozone is a primary trading partner for Sweden. Tracking EUR/SEK helps:
      - Evaluate Sweden's trade competitiveness with EU countries
      - Assess inflationary pressures from Euro-denominated imports

    Args:
        from_date (date): Start date (YYYY-MM-DD).
        to_date (Optional[date]): End date; if None, latest data is retrieved.

    Returns:
        ExchangeRateData with a list of observations (date, value).

    Usage:
        - Combine with policy rate data to explore monetary policy alignment vs. ECB
        - Compare EUR/SEK volatility to USD/SEK or GBP/SEK
    """
    eur_series_id = "SEKEURPMI"  # example ID for EUR, adapt if necessary
    observations = await fetch_observations(eur_series_id, from_date, to_date)
    return ExchangeRateData(series_id=eur_series_id, observations=observations)


async def get_gbp_exchange_rate(
    from_date: date, to_date: Optional[date] = None
) -> ExchangeRateData:
    """
    Retrieve GBP/SEK exchange rate data from the SWEA API.

    Post-Brexit, GBP can show distinct movement from EUR. Analysts often track GBP/SEK to:
      - Assess UK-Sweden trade competitiveness
      - Monitor how political and macro shocks affect currency valuations

    Args:
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date.

    Returns:
        ExchangeRateData with a list of GBP/SEK observations.

    Example:
        >>> gbp_data = await get_gbp_exchange_rate(date(2023, 1, 1))
        >>> print(gbp_data.observations[-1].date, gbp_data.observations[-1].value)

    Disclaimer:
        - Riksbanken’s disclaimers apply (indicative only, do not use for transactions).
    """
    gbp_series_id = "SEKGBPPMI"  # example ID
    observations = await fetch_observations(gbp_series_id, from_date, to_date)
    return ExchangeRateData(series_id=gbp_series_id, observations=observations)


async def get_mortgage_rate(
    from_date: date, to_date: Optional[date] = None
) -> InterestRateData:
    """
    Retrieve average Swedish mortgage (housing loan) interest rate data.

    Mortgage rates affect consumption, housing demand, and are a key element in household debt analysis.

    Args:
        from_date (date): Start date in YYYY-MM-DD format.
        to_date (Optional[date]): End date or None for the latest available data.

    Returns:
        InterestRateData: Contains a list of daily observations.

    Example:
        >>> from datetime import date
        >>> mortgage_data = await get_mortgage_rate(date(2022, 1, 1))
        >>> for m in mortgage_data.observations:
        ...     print(m.date, m.value)

    Usage:
        - House price bubble analysis
        - Tracking changes in lending conditions after Riksbank rate decisions
    """
    # Example ID; replace with the actual mortgage rate series used by the Riksbank
    mortgage_rate_series_id = "SEKHOUPMI"
    observations = await fetch_observations(mortgage_rate_series_id, from_date, to_date)
    return InterestRateData(observations=observations)


async def get_calendar_days(
    from_date: date, to_date: Optional[date] = None
) -> list[CalendarDay]:
    """
    Retrieve Swedish calendar days from the SWEA API.

    The Riksbank marks which days are Swedish bank days vs. weekends/holidays.
    This helps analysts confirm trading days or settlement days for financial instruments.

    Args:
        from_date (date): Start date.
        to_date (Optional[date]): End date; if None, fetch up to the present date.

    Returns:
        list[CalendarDay] with fields like:
            - calendarDate (str)
            - swedishBankday (bool)
            - ultimo (bool) if it's the last bank day of the month
            - weekYear, weekNumber, quarterNumber

    Example:
        >>> days = await get_calendar_days(date(2023, 1, 1), date(2023, 1, 31))
        >>> for d in days:
        ...     print(d.calendarDate, d.swedishBankday, d.ultimo)
    """
    endpoint = f"CalendarDays/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"

    response = await swea_request(endpoint)
    if not response:
        return []

    return [CalendarDay.model_validate(item) for item in response]


async def get_cross_rates(
    series_id1: str, series_id2: str, from_date: date, to_date: Optional[date] = None
) -> list[CrossRate]:
    """
    Retrieve cross rates between two foreign currency series (via SEK).

    The Riksbank’s cross rate is derived as:
      rate( currency1 / currency2 ) = (currency1 / SEK) / (currency2 / SEK)

    Args:
        series_id1 (str): Base currency’s series ID, e.g. "SEKUSDPMI".
        series_id2 (str): Quote currency’s series ID, e.g. "SEKEURPMI".
        from_date (date): Start date.
        to_date (Optional[date]): End date or None for latest.

    Returns:
        list[CrossRate]: Each entry with date and calculated cross rate value.

    Example:
        >>> # Cross between USD and EUR from 2024-01-23 to 2024-02-15
        >>> rates = await get_cross_rates("SEKUSDPMI", "SEKEURPMI", date(2024,1,23), date(2024,2,15))
        >>> for r in rates:
        ...     print(r.date, r.value)

    Note:
        - If you need a reversed cross rate, simply swap series_id1 and series_id2, or compute 1/value.
    """
    endpoint = f"CrossRates/{series_id1}/{series_id2}/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"

    response = await swea_request(endpoint)
    if not response:
        return []

    return [CrossRate.model_validate(item) for item in response]


async def get_cross_rate_aggregates(
    series_id1: str,
    series_id2: str,
    aggregation: str,
    from_date: date,
    to_date: Optional[date] = None,
) -> list[CrossRateAggregate]:
    """
    Retrieve aggregated cross rates (W, M, Q, Y) between two currency series.

    This is particularly useful for analyzing average monthly cross-currency trends,
    or for macroeconomic studies correlating currency pairs over time.

    Args:
        series_id1 (str): Base currency’s series ID (e.g. "SEKUSDPMI").
        series_id2 (str): Quote currency’s series ID (e.g. "SEKEURPMI").
        aggregation (str): One of "W", "M", "Q", "Y".
        from_date (date): Start date.
        to_date (Optional[date]): End date, else up to the latest data.

    Returns:
        list[CrossRateAggregate] with fields (year, seqNr, value).

    Example:
        >>> # Get quarterly aggregates for USD/EUR cross from 2023 onward
        >>> q_data = await get_cross_rate_aggregates("SEKUSDPMI", "SEKEURPMI", "Q", date(2023,1,1))
        >>> for d in q_data:
        ...     print(d.year, d.seqNr, d.value)
    """
    endpoint = f"CrossRateAggregates/{series_id1}/{series_id2}/{aggregation}/{from_date.isoformat()}"
    if to_date:
        endpoint += f"/{to_date.isoformat()}"

    response = await swea_request(endpoint)
    if not response:
        return []

    return [CrossRateAggregate.model_validate(item) for item in response]


async def list_groups(language: str = "en") -> dict[str, Any]:
    """
    Retrieve the hierarchy of all Groups from the SWEA API.

    Each Group is an organizational unit containing one or more Series. Groups can be nested.

    Args:
        language (str): "en" (default) or "sv" for Swedish.

    Returns:
        dict[str, Any]: Nested structure describing group IDs, names, descriptions, child groups.

    Example:
        >>> all_groups = await list_groups()
        >>> print(all_groups.keys())
    """
    params: dict[str, str] = {"language": language}
    response = await swea_request("groups", params)
    return response or {}


async def get_group_details(group_id: int, language: str = "en") -> dict[str, Any]:
    """
    Get details for a specific Group by its ID.

    Args:
        group_id (int): The group identifier (int).
        language (str): "en" or "sv".

    Returns:
        dict[str, Any]: Contains info about the group, including child groups (if any).

    Example:
        >>> details = await get_group_details(130, "sv")
        >>> print(details["name"])
        "Valutor mot svenska kronor"
    """
    endpoint = f"Groups/{group_id}"
    params: dict[str, str] = {"language": language}
    response = await swea_request(endpoint, params)
    return response or {}


async def list_series(language: str = "en") -> list[dict[str, Any]]:
    """
    List all available Series in the SWEA API.

    Each Series entry typically includes:
      - seriesId
      - source
      - shortDescription
      - midDescription
      - longDescription
      - groupId
      - observationMaxDate
      - observationMinDate
      - seriesClosed

    Args:
        language (str): "en" or "sv" (default "en").

    Returns:
        list[dict[str, Any]]: A list of dictionaries, one per Series.

    Example:
        >>> series_list = await list_series()
        >>> print(series_list[0]["seriesId"])
    """
    params: dict[str, str] = {"language": language}
    response = await swea_request("series", params)
    if not response:
        return []
    if isinstance(response, list):
        return response
    return []


async def get_series_info(
    series_id: str, language: str = "en"
) -> Optional[dict[str, Any]]:
    """
    Retrieve metadata about a specific Series.

    For a given seriesId, learn:
      - Full descriptions
      - Data range (minDate, maxDate)
      - Whether the series is closed

    Args:
        series_id (str): e.g. "SEKUSDPMI"
        language (str): "en" or "sv".

    Returns:
        dict[str, Any] or None: The series info if found, else None.

    Example:
        >>> info = await get_series_info("SEKUSDPMI")
        >>> print(info["longDescription"])
        "US Dollar to Swedish Krona exchange rate..."
    """
    endpoint = f"Series/{series_id}"
    params: dict[str, str] = {"language": language}
    response = await swea_request(endpoint, params)
    return response if response else None


async def list_exchange_rate_series(language: str = "en") -> list[dict[str, Any]]:
    """
    List all available exchange rate series (i.e. currencies against SEK) in the SWEA API.

    Args:
        language (str): "en" (default) or "sv".

    Returns:
        list[dict[str, Any]]: Each item is a series dict with keys like seriesId, shortDescription, etc.

    Example:
        >>> fx_series = await list_exchange_rate_series()
        >>> for fx in fx_series:
        ...     print(fx["seriesId"], fx["shortDescription"])
    """
    endpoint = "Series/ExchangeRateSeries"
    params: dict[str, str] = {"language": language}
    response = await swea_request(endpoint, params)
    if not response:
        return []
    if isinstance(response, list):
        return response
    return []


# ------------------------------
# Combination & Transformation Tools
# ------------------------------


def merge_series_on_date(
    series_a: list[Observation], series_b: list[Observation]
) -> list[tuple[str, float, float]]:
    """
    Merge two observation series by date, returning tuples of (date, valueA, valueB).

    Useful for:
     - Comparing different rates or currency pairs side by side
     - Calculating spreads or relative changes between two time series

    Args:
        series_a (list[Observation]): The first time series.
        series_b (list[Observation]): The second time series.

    Returns:
        list of (str, float, float): For each matching date, a tuple of (date, valA, valB).
                                     If a date is missing in one series, it is not included.

    Example:
        >>> # Suppose you fetch policy rate and inflation observations
        >>> merged = merge_series_on_date(policy_rate_observations, inflation_observations)
        >>> for row in merged[:5]:
        ...     print(row)
        ('2023-01-02', 2.5, 0.5)

    Implementation Detail:
        - Both series should be sorted by date for consistent merges
        - We do an O(n+m) pass to align them by date
    """
    # Convert to dict for faster membership lookups
    map_b = {obs.date: obs.value for obs in series_b}
    out: list[tuple[str, float, float]] = []
    for obs_a in series_a:
        val_b = map_b.get(obs_a.date)
        if val_b is not None:
            out.append((obs_a.date, obs_a.value, val_b))
    return out


def compute_percentage_change(
    series: list[Observation], periods: int = 1
) -> list[Observation]:
    """
    Compute the percentage change of a time series over a given number of prior observations.

    This is commonly used for:
      - Year-over-year changes if data is monthly and you pass periods=12
      - Month-over-month changes if data is monthly with periods=1
      - Daily returns if data is daily with periods=1

    Args:
        series (list[Observation]): A list of Observations with (date, value).
        periods (int): The lag to use in the percentage change calculation.

    Returns:
        list[Observation]: A new series of Observations where value is the % change vs. `periods` steps before.
                           The first `periods` points will be omitted because no previous data is available.

    Formula:
        pct_change = (current_value - previous_value) / previous_value * 100

    Example:
        >>> # Suppose you have monthly inflation data in 'inflation_series'
        >>> yoy = compute_percentage_change(inflation_series, 12)
        >>> for obs in yoy[:5]:
        ...     print(obs.date, obs.value)

    Warning:
        - If previous_value is 0 or None, the % change is not defined. We skip or return no observation for that date.
        - The returned list is shorter than the original by `periods`.
    """
    out: list[Observation] = []
    if len(series) <= periods:
        return out

    # Sort by date just in case
    sorted_series = sorted(series, key=lambda x: x.date)

    for i in range(periods, len(sorted_series)):
        curr = sorted_series[i]
        prev = sorted_series[i - periods]
        if prev.value and prev.value != 0:
            pct_change = (curr.value - prev.value) / prev.value * 100
            out.append(Observation(date=curr.date, value=pct_change))

    return out
