"""
Tools for working with the Riksbank's SWESTR data.
"""

from datetime import date

from riksbank_mcp.models import InterestRateData, Observation
from riksbank_mcp.services.swestr_api import swestr_request


async def fetch_interest_rate(
    from_date: date | None = None, to_date: date | None = None
) -> list[Observation]:
    """
    Fetch SWESTR interest rate data from the Riksbank API.

    Retrieves SWESTR (Swedish krona Short Term Rate) data for the specified date range.

    Args:
        from_date (date | None  = None): Optional start date for the data range
        to_date (date | None  = None): Optional end date for the data range

    Returns:
        list[Observation]: A list of SWESTR rate observations with dates and values

    Example:
        >>> from datetime import date
        >>> start_date = date(2022, 1, 1)
        >>> end_date = date(2022, 12, 31)
        >>> rates = await fetch_interest_rate(start_date, end_date)
    """
    params: dict[str, str] = {}

    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()

    response = await swestr_request("rates", params)
    raw_rates = response.get("rates", [])

    return [
        Observation(
            date=rate.get("date", rate.get("dt", "")),
            value=float(rate.get("value", rate.get("val", 0.0))),
        )
        for rate in raw_rates
    ]


async def get_swestr(
    from_date: date | None = None, to_date: date | None = None
) -> InterestRateData:
    """
    Retrieve the SWESTR (Swedish krona Short Term Rate) over a specified period.

    SWESTR reflects the actual transaction-based short term rate in the Swedish money market.

    Args:
        from_date (date | None  = None): Start date for the period.
        to_date (date | None  = None): End date for the period.

    Returns:
        InterestRateData: A model containing SWESTR rate observations.

    Usage Example:
        >>> from datetime import date
        >>> swestr_data = await get_swestr(date(2023, 1, 1))
        >>> for obs in swestr_data.observations:
        ...     print(f"Rate on {obs.date} = {obs.value}%")

    Frequency & Range:
        - Typically observed daily.

    Disclaimer:
        SWESTR is relatively new; use historical trends with caution.
    """
    observations = await fetch_interest_rate(from_date, to_date)
    return InterestRateData(observations=observations)


async def get_latest_swestr() -> Observation:
    """
    Retrieve the latest published SWESTR rate.

    This function returns the most recent SWESTR observation, providing a snapshot of current money market conditions.

    Returns:
        Observation: A data point containing the date and rate.

    Usage Example:
        >>> latest_rate = await get_latest_swestr()
        >>> print("Latest SWESTR:", latest_rate.date, latest_rate.value)

    Disclaimer:
        This is a single-point observation; for trend analysis, refer to the full SWESTR series.
    """
    response = await swestr_request("latest")
    rate_data = response.get("rate", {})

    return Observation(
        date=rate_data.get("date", rate_data.get("dt", "")),
        value=float(rate_data.get("value", rate_data.get("val", 0.0))),
    )


async def get_swestr_averages(
    from_date: date | None = None, to_date: date | None = None
) -> InterestRateData:
    """
    Retrieve compounded SWESTR averages over a specified period.

    These backward-looking averages (covering various periods) smooth out daily volatility
    and help in analyzing short-term interest trends.

    Args:
        from_date (date | None  = None): Start date of the period.
        to_date (date | None  = None): End date of the period.

    Returns:
        InterestRateData: A model containing aggregated SWESTR average rate observations.

    Usage Example:
        >>> swestr_averages = await get_swestr_averages()
        >>> print("First average entry:", swestr_averages.observations[0])

    Disclaimer:
        For specific period averages (e.g., 1-week or 1-month), use the dedicated functions.
    """
    params: dict[str, str] = {}

    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()

    response = await swestr_request("averages", params)
    raw_rates = response.get("averages", [])

    observations = [
        Observation(
            date=rate.get("date", rate.get("dt", "")),
            value=float(rate.get("value", rate.get("val", 0.0))),
        )
        for rate in raw_rates
    ]

    return InterestRateData(observations=observations)


async def get_swestr_1week(
    from_date: date | None = None, to_date: date | None = None
) -> InterestRateData:
    """
    Retrieve the 1-week compounded SWESTR average.

    This average reflects the SEK funding cost compounded over a one-week horizon.

    Args:
        from_date (date | None  = None): Start date for filtering.
        to_date (date | None  = None): End date for filtering.

    Returns:
        InterestRateData: A model containing 1-week SWESTR average observations.

    Usage Example:
        >>> from datetime import date
        >>> one_week_avg = await get_swestr_1week(date(2023,1,1), date(2023,2,1))
        >>> for obs in one_week_avg.observations:
        ...     print(f"{obs.date}: {obs.value}%")

    Disclaimer:
        Although less volatile than daily rates, 1-week averages may still exhibit short-term shifts.
    """
    params = {"period": "1week"}

    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()

    response = await swestr_request("averages", params)
    raw_rates = response.get("averages", [])

    observations = [
        Observation(
            date=rate.get("date", rate.get("dt", "")),
            value=float(rate.get("value", rate.get("val", 0.0))),
        )
        for rate in raw_rates
    ]

    return InterestRateData(observations=observations)


async def get_swestr_1month(
    from_date: date | None = None, to_date: date | None = None
) -> InterestRateData:
    """
    Retrieve the 1-month compounded SWESTR average.

    The 1-month average smooths daily fluctuations and is used for analyzing monthly monetary conditions.

    Args:
        from_date (date | None  = None): The inclusive start date.
        to_date (date | None  = None): The inclusive end date.

    Returns:
        InterestRateData: A model containing 1-month SWESTR average observations.

    Usage Example:
        >>> one_month_avg = await get_swestr_1month()
        >>> print("Latest 1-month average:", one_month_avg.observations[-1])

    Disclaimer:
        Monthly averages may mask short-term volatility; for high-frequency trading, daily rates are preferable.
    """
    params = {"period": "1month"}

    if from_date:
        params["from"] = from_date.isoformat()
    if to_date:
        params["to"] = to_date.isoformat()

    response = await swestr_request("averages", params)
    raw_rates = response.get("averages", [])

    observations = [
        Observation(
            date=rate.get("date", rate.get("dt", "")),
            value=float(rate.get("value", rate.get("val", 0.0))),
        )
        for rate in raw_rates
    ]

    return InterestRateData(observations=observations)
"""
Tools for working with the Riksbank's SWESTR (Swedish krona Short Term Rate) data.
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

import httpx

from riksbank_mcp.models import Observation, InterestRateData


async def fetch_interest_rate(
    from_date: date, to_date: Optional[date] = None
) -> List[Observation]:
    """
    Fetch SWESTR interest rate data from the Riksbank API.

    Args:
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date; if None, fetches up to the latest available data.

    Returns:
        List[Observation]: A list of observations with date and value.
    """
    base_url = "https://swestr.riksbank.se/api/v1/rates"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            observations = []
            for item in data.get("data", []):
                if isinstance(item, dict) and "date" in item and "value" in item:
                    observations.append(
                        Observation(
                            date=item["date"],
                            value=float(item["value"])
                        )
                    )
            return observations
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                # No data available for the specified period
                return []
            raise
        except Exception as e:
            print(f"Error fetching SWESTR data: {e}")
            return []


async def get_swestr(
    from_date: date, to_date: Optional[date] = None
) -> InterestRateData:
    """
    Retrieve SWESTR (Swedish krona Short Term Rate) data.

    SWESTR is the Riksbank's transaction-based reference rate in Swedish kronor,
    calculated based on transactions in the overnight market.

    Args:
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date; if None, fetches up to the latest available data.

    Returns:
        InterestRateData: A model containing a list of daily SWESTR observations.

    Example:
        >>> from datetime import date
        >>> swestr_data = await get_swestr(date(2023, 1, 1))
        >>> for obs in swestr_data.observations:
        ...     print(f"{obs.date}: {obs.value}%")
    """
    observations = await fetch_interest_rate(from_date, to_date)
    return InterestRateData(observations=observations)


async def get_latest_swestr() -> Optional[Observation]:
    """
    Retrieve the latest published SWESTR rate.

    Returns:
        Optional[Observation]: The latest SWESTR observation, or None if not available.

    Example:
        >>> latest = await get_latest_swestr()
        >>> if latest:
        ...     print(f"Latest SWESTR ({latest.date}): {latest.value}%")
    """
    base_url = "https://swestr.riksbank.se/api/v1/rates/latest"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url)
            response.raise_for_status()
            data = response.json()
            
            if "data" in data and data["data"]:
                item = data["data"]
                if "date" in item and "value" in item:
                    return Observation(
                        date=item["date"],
                        value=float(item["value"])
                    )
            return None
        except Exception as e:
            print(f"Error fetching latest SWESTR: {e}")
            return None


async def get_swestr_averages(
    from_date: date, to_date: Optional[date] = None
) -> InterestRateData:
    """
    Retrieve SWESTR average rates.

    The Riksbank calculates and publishes compounded average rates based on SWESTR.
    These averages are useful for financial contracts with longer terms.

    Args:
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date; if None, fetches up to the latest available data.

    Returns:
        InterestRateData: A model containing a list of SWESTR average observations.

    Example:
        >>> from datetime import date
        >>> averages = await get_swestr_averages(date(2023, 1, 1))
        >>> for obs in averages.observations:
        ...     print(f"{obs.date}: {obs.value}%")
    """
    base_url = "https://swestr.riksbank.se/api/v1/averages"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            observations = []
            for item in data.get("data", []):
                if isinstance(item, dict) and "date" in item and "value" in item:
                    observations.append(
                        Observation(
                            date=item["date"],
                            value=float(item["value"])
                        )
                    )
            return InterestRateData(observations=observations)
        except Exception as e:
            print(f"Error fetching SWESTR averages: {e}")
            return InterestRateData(observations=[])


async def get_swestr_1week(
    from_date: date, to_date: Optional[date] = None
) -> InterestRateData:
    """
    Retrieve 1-week SWESTR average rates.

    The 1-week SWESTR average is a compounded average of SWESTR over a 1-week period.
    This is useful for financial contracts with a 1-week term.

    Args:
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date; if None, fetches up to the latest available data.

    Returns:
        InterestRateData: A model containing a list of 1-week SWESTR average observations.

    Example:
        >>> from datetime import date
        >>> one_week = await get_swestr_1week(date(2023, 1, 1))
        >>> for obs in one_week.observations:
        ...     print(f"{obs.date}: {obs.value}%")
    """
    base_url = "https://swestr.riksbank.se/api/v1/averages/1week"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            observations = []
            for item in data.get("data", []):
                if isinstance(item, dict) and "date" in item and "value" in item:
                    observations.append(
                        Observation(
                            date=item["date"],
                            value=float(item["value"])
                        )
                    )
            return InterestRateData(observations=observations)
        except Exception as e:
            print(f"Error fetching 1-week SWESTR averages: {e}")
            return InterestRateData(observations=[])


async def get_swestr_1month(
    from_date: date, to_date: Optional[date] = None
) -> InterestRateData:
    """
    Retrieve 1-month SWESTR average rates.

    The 1-month SWESTR average is a compounded average of SWESTR over a 1-month period.
    This is useful for financial contracts with a 1-month term.

    Args:
        from_date (date): Start date for the query.
        to_date (Optional[date]): End date; if None, fetches up to the latest available data.

    Returns:
        InterestRateData: A model containing a list of 1-month SWESTR average observations.

    Example:
        >>> from datetime import date
        >>> one_month = await get_swestr_1month(date(2023, 1, 1))
        >>> for obs in one_month.observations:
        ...     print(f"{obs.date}: {obs.value}%")
    """
    base_url = "https://swestr.riksbank.se/api/v1/averages/1month"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            observations = []
            for item in data.get("data", []):
                if isinstance(item, dict) and "date" in item and "value" in item:
                    observations.append(
                        Observation(
                            date=item["date"],
                            value=float(item["value"])
                        )
                    )
            return InterestRateData(observations=observations)
        except Exception as e:
            print(f"Error fetching 1-month SWESTR averages: {e}")
            return InterestRateData(observations=[])
