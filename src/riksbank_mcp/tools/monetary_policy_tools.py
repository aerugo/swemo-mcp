"""
Tools for working with the Riksbank's Monetary Policy data.
"""

import logging
from typing import List, Optional, Dict, Any

from riksbank_mcp.models import (
    ForecastResult, 
    Observation, 
    PolicyRound, 
    SeriesInfo,
    MonetaryPolicyResponse,
    ForecastSeries
)
from riksbank_mcp.services.monetary_policy_api import riksbanken_request

# Set up logging
logger = logging.getLogger(__name__)

async def list_policy_rounds() -> List[PolicyRound]:
    """
    List all available monetary policy rounds from the Riksbank.

    Retrieves a comprehensive list of all monetary policy rounds, including their
    identifiers, dates, and descriptions when available.

    Returns:
        List[PolicyRound]: A list of policy rounds with their metadata.

    Example:
        >>> rounds = await list_policy_rounds()
        >>> for r in rounds:
        ...     print(f"{r.id}: {r.date}")
    """
    response = await riksbanken_request("forecasts/policy_rounds")
    
    try:
        # Validate response against expected schema
        policy_response = MonetaryPolicyResponse(data=response.get("data", []))
        rounds_data = policy_response.data
        
        # Process the data into PolicyRound objects
        result = []
        for round_data in rounds_data:
            if isinstance(round_data, dict):
                result.append(
                    PolicyRound(
                        id=round_data.get("id", ""),
                        date=round_data.get("date", ""),
                        description=round_data.get("description")
                    )
                )
            else:
                # Handle the case where it's just a string
                result.append(
                    PolicyRound(
                        id=str(round_data),
                        date="",
                        description=None
                    )
                )
        return result
    except Exception as e:
        logger.error(f"Error processing policy rounds: {e}")
        return []


async def list_series_ids() -> List[SeriesInfo]:
    """
    List all available series IDs for forecasts from the Riksbank.

    Retrieves metadata about all economic data series available through the
    Monetary Policy API, including identifiers, names, and descriptions.

    Returns:
        List[SeriesInfo]: A list of series information objects with metadata.

    Example:
        >>> series_list = await list_series_ids()
        >>> for series in series_list:
        ...     print(f"{series.id}: {series.name}")
    """
    response = await riksbanken_request("forecasts/series_ids")
    
    try:
        # Validate response against expected schema
        policy_response = MonetaryPolicyResponse(data=response.get("data", []))
        series_data = policy_response.data
        
        # Process the data into SeriesInfo objects
        result = []
        for series in series_data:
            if isinstance(series, dict):
                metadata = {
                    k: v for k, v in series.items() 
                    if k not in ["series_id", "name", "description", "unit"]
                }
                
                result.append(
                    SeriesInfo(
                        id=series.get("series_id", ""),
                        name=series.get("name", ""),
                        description=series.get("description"),
                        unit=series.get("unit"),
                        metadata=metadata if metadata else None
                    )
                )
        return result
    except Exception as e:
        logger.error(f"Error processing series IDs: {e}")
        return []


async def get_forecast_data(
    series_id: str, policy_round: Optional[str] = None
) -> ForecastResult:
    """
    Fetch forecast data for a given series from the Riksbank Monetary Policy API.

    Retrieves all forecast vintages for the specified series ID. Optionally,
    if a policy_round is provided, only the vintages matching that round are returned.

    Args:
        series_id (str): The unique identifier for the economic series (e.g. "GDP").
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing series data and observations.

    Example:
        >>> result = await get_forecast_data("SEQGDPNAYCA", "2023:4")
        >>> for obs in result.observations:
        ...     print(f"{obs.date}: {obs.value}")
    """
    params: Dict[str, str] = {"series": series_id}
    if policy_round:
        params["policy_round_name"] = policy_round

    response = await riksbanken_request("forecasts", params)
    
    try:
        # Validate response against expected schema
        policy_response = MonetaryPolicyResponse(data=response.get("data", []))
        raw_items = policy_response.data
        
        # Process the data into ForecastSeries objects
        observations: List[Observation] = []
        
        for series_item in raw_items:
            if not isinstance(series_item, dict):
                continue
                
            # Extract observations from each vintage's observations array
            for vintage in series_item.get("vintages", []):
                if not isinstance(vintage, dict):
                    continue
                    
                for obs_item in vintage.get("observations", []):
                    if not isinstance(obs_item, dict):
                        continue
                        
                    try:
                        # Ensure value is a number
                        value = obs_item.get("value")
                        if value == "":  # Handle empty string values
                            value = 0.0
                        else:
                            value = float(value)
                            
                        observations.append(
                            Observation(
                                date=obs_item.get("dt", ""),  # Use "dt" for date
                                value=value,
                            )
                        )
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid observation value: {e}")
                        continue

        return ForecastResult(
            series_id=series_id, policy_round=policy_round, observations=observations
        )
    except Exception as e:
        logger.error(f"Error processing forecast data: {e}")
        return ForecastResult(series_id=series_id, policy_round=policy_round, observations=[])


async def get_gdp_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's Gross Domestic Product (GDP).

    Args:
        policy_round (Optional[str]): If provided, filters forecasts to the specified round.

    Returns:
        ForecastResult: Model containing GDP forecast data (annual percentage change).

    Usage Example:
        >>> gdp_forecast = await get_gdp_data("2023:4")
        >>> for obs in gdp_forecast.observations:
        ...     print(f"Date: {obs.date}, GDP forecast: {obs.value}")
    """
    # Commonly used ID for GDP yoy growth (calendar-adjusted):
    series_id = "SEQGDPNAYCA"
    return await get_forecast_data(series_id, policy_round)


async def get_unemployment_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's unemployment rate (seasonally adjusted).

    Args:
        policy_round (Optional[str]): If provided, returns data for the specified round.

    Returns:
        ForecastResult: Model containing unemployment rate forecasts.
    """
    series_id = "SEQLABUEASA"  # Unemployment rate (seasonally adjusted)
    return await get_forecast_data(series_id, policy_round)


async def get_cpi_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's Consumer Price Index (CPI).

    Args:
        policy_round (Optional[str]): If provided, filters data to a specific policy round.

    Returns:
        ForecastResult: Model containing forecasted CPI data (annual percentage changes).
    """
    series_id = "SECPIYRCA"  # CPI series ID (annual percentage change)
    return await get_forecast_data(series_id, policy_round)


async def get_cpif_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve Sweden's CPIF (Consumer Price Index with Fixed Interest Rate) forecast.

    Args:
        policy_round (Optional[str]): Monetary policy round identifier.

    Returns:
        ForecastResult: CPIF forecast data.
    """
    series_id = "SECPIFYRCA"  # CPIF series ID (annual percentage change)
    return await get_forecast_data(series_id, policy_round)


async def get_cpif_ex_energy_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve Sweden's CPIF excluding energy forecast data.

    Args:
        policy_round (Optional[str]): Filter forecasts to a specific round if provided.

    Returns:
        ForecastResult: Model of CPIF ex-energy forecast data.
    """
    series_id = (
        "SECPIFXEYRCA"  # CPIF excluding energy series ID (annual percentage change)
    )
    return await get_forecast_data(series_id, policy_round)


async def get_hourly_labour_cost_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's hourly labour cost.

    Args:
        policy_round (Optional[str]): If provided, returns data from the specified round.

    Returns:
        ForecastResult: Forecast data for hourly labour costs.
    """
    series_id = "SEHLCYRCA"  # Hourly labour cost series ID
    return await get_forecast_data(series_id, policy_round)


async def get_hourly_wage_na_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's hourly wage (National Accounts).

    Args:
        policy_round (Optional[str]): Specific monetary policy round to filter the data.

    Returns:
        ForecastResult: Hourly wage NA forecast data.
    """
    series_id = "SEHWNAYRCA"  # Hourly wage (NA) series ID
    return await get_forecast_data(series_id, policy_round)


async def get_hourly_wage_nmo_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's hourly wage (National Mediation Office).

    Args:
        policy_round (Optional[str]): If specified, filters data to the desired round.

    Returns:
        ForecastResult: NMO-based hourly wage forecasts.
    """
    series_id = "SEHWNMOYRCA"  # Hourly wage (NMO) series ID
    return await get_forecast_data(series_id, policy_round)


async def get_nominal_exchange_rate_kix_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's nominal exchange rate (KIX).

    Args:
        policy_round (Optional[str]): Optional policy round identifier.

    Returns:
        ForecastResult: KIX exchange rate forecasts.
    """
    series_id = "SEKIXYRCA"  # KIX exchange rate series ID
    return await get_forecast_data(series_id, policy_round)


async def get_population_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's population.

    Args:
        policy_round (Optional[str]): Optional filter for a specific forecast cycle.

    Returns:
        ForecastResult: Population forecast data with (date, value) pairs.
    """
    series_id = "SEPOPYRCA"  # Population series ID
    return await get_forecast_data(series_id, policy_round)


async def get_employed_persons_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for the total number of employed persons in Sweden.

    Args:
        policy_round (Optional[str]): If provided, returns data from the specified round.

    Returns:
        ForecastResult: Employment forecast data.
    """
    series_id = "SEEMPYRCA"  # Employed persons series ID
    return await get_forecast_data(series_id, policy_round)


async def get_labour_force_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for the size of the Swedish labour force.

    Args:
        policy_round (Optional[str]): Filter for a specific forecast cycle if desired.

    Returns:
        ForecastResult: Labour force forecast data.
    """
    series_id = "SELABFYRCA"  # Labour force series ID
    return await get_forecast_data(series_id, policy_round)


# -----------------------
# Additional interesting series
# -----------------------


async def get_gdp_gap_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for the Swedish GDP gap.

    The GDP gap measures the deviation of actual GDP from its estimated potential,
    providing insight into whether the economy is operating above or below capacity.

    Args:
        policy_round (Optional[str]): Filter data to a specific monetary policy round if provided.

    Returns:
        ForecastResult: A validated model containing GDP gap forecasts (in percent).

    Usage Example:
        >>> gdp_gap = await get_gdp_gap_data("2024:1")
        >>> for obs in gdp_gap.observations:
        ...     print(f"{obs.date}: {obs.value}% deviation from potential")
    """
    series_id = "SEQGDPGAPYSA"  # GDP gap (seasonally & calendar adjusted)
    return await get_forecast_data(series_id, policy_round)


async def get_policy_rate_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for the Swedish Policy Rate (Riksbank repo rate).

    The policy rate is a key tool for monetary policy decisions, influencing
    market interest rates and overall liquidity.

    Args:
        policy_round (Optional[str]): Filter data to a specific round if desired.

    Returns:
        ForecastResult: A validated model containing the policy rate forecasts (in percent).

    Usage Example:
        >>> policy_rate = await get_policy_rate_data("2023:4")
        >>> print("Latest forecasted repo rate:", policy_rate.observations[-1].value)
    """
    series_id = "SEQRATENAYNA"  # Policy Rate, quarterly mean values
    return await get_forecast_data(series_id, policy_round)


async def get_general_government_net_lending_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's general government net lending.

    This series represents the net lending/borrowing of the public sector and is
    typically expressed as a percentage of GDP.

    Args:
        policy_round (Optional[str]): Optionally filter to a specific forecast round.

    Returns:
        ForecastResult: A validated model containing net lending data (share of GDP).

    Usage Example:
        >>> gov_lending = await get_general_government_net_lending_data("2024:1")
        >>> for obs in gov_lending.observations:
        ...     print(f"{obs.date}: {obs.value}% of GDP")
    """
    series_id = "SEAPBSNAYNA"  # General government net lending, % of GDP
    return await get_forecast_data(series_id, policy_round)
