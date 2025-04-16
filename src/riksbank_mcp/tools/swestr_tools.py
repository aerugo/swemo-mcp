"""
Tools for working with the Riksbank's SWESTR (Swedish krona Short Term Rate) data.
"""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional

from riksbank_mcp.models import InterestRateData, Observation
from riksbank_mcp.services.swestr_api import swestr_request


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
    endpoint = "rates"
    params: Dict[str, str] = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    try:
        data = await swestr_request(endpoint, params)

        observations = []
        for item in data.get("data", []):
            if isinstance(item, dict) and "date" in item and "value" in item:
                observations.append(
                    Observation(date=item["date"], value=float(item["value"]))
                )
        return observations
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
    endpoint = "rates/latest"

    try:
        data = await swestr_request(endpoint)

        if "data" in data and data["data"]:
            item = data["data"]
            if "date" in item and "value" in item:
                return Observation(date=item["date"], value=float(item["value"]))
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
    endpoint = "averages"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    try:
        data = await swestr_request(endpoint, params)

        observations = []
        for item in data.get("data", []):
            if isinstance(item, dict) and "date" in item and "value" in item:
                observations.append(
                    Observation(date=item["date"], value=float(item["value"]))
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
    endpoint = "averages/1week"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    try:
        data = await swestr_request(endpoint, params)

        observations = []
        for item in data.get("data", []):
            if isinstance(item, dict) and "date" in item and "value" in item:
                observations.append(
                    Observation(date=item["date"], value=float(item["value"]))
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
    endpoint = "averages/1month"
    params = {"from": from_date.isoformat()}
    if to_date:
        params["to"] = to_date.isoformat()

    try:
        data = await swestr_request(endpoint, params)

        observations = []
        for item in data.get("data", []):
            if isinstance(item, dict) and "date" in item and "value" in item:
                observations.append(
                    Observation(date=item["date"], value=float(item["value"]))
                )
        return InterestRateData(observations=observations)
    except Exception as e:
        print(f"Error fetching 1-month SWESTR averages: {e}")
        return InterestRateData(observations=[])
