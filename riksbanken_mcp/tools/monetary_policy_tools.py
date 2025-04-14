"""
Tools for working with the Riksbank's Monetary Policy data.
"""
from typing import Dict, List, Any, Optional
from riksbanken_mcp.services.monetary_policy_api import riksbanken_request
from riksbanken_mcp.models import ForecastResult, Observation, PolicyRound, SeriesInfo

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
        >>>     print(f"{r.id}: {r.date}")
    """
    response = await riksbanken_request("policy-rounds")
    rounds_data = response["policyRounds"]
    
    return [PolicyRound(
        id=round_data.get("id", ""),
        date=round_data.get("date", ""),
        description=round_data.get("description", None)
    ) for round_data in rounds_data]

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
        >>>     print(f"{series.id}: {series.name}")
    """
    response = await riksbanken_request("series")
    series_data = response["series"]
    
    return [SeriesInfo(
        id=series.get("id", ""),
        name=series.get("name", ""),
        description=series.get("description", None),
        unit=series.get("unit", None)
    ) for series in series_data]

async def get_forecast_data(series_id: str, policy_round: Optional[str] = None) -> ForecastResult:
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
        >>>     print(f"{obs.date}: {obs.value}")
    """
    params = {"seriesid": series_id}
    if policy_round:
        params["policyround"] = policy_round
        
    response = await riksbanken_request("forecasts", params)
    raw_items = response.get("forecasts", [])
    observations = []
    
    for item in raw_items:
        # Convert API response to Observation model
        observations.append(Observation(
            date=item.get("date", item.get("dt", "")),
            value=float(item.get("value", item.get("val", 0.0)))
        ))
    
    return ForecastResult(
        series_id=series_id,
        policy_round=policy_round,
        observations=observations
    )

async def get_gdp_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Get GDP forecast data from the Riksbank.
    
    Retrieves the Gross Domestic Product (GDP) forecast data for Sweden.
    
    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").
        
    Returns:
        ForecastResult: A validated model containing GDP data and observations.
        
    Example:
        >>> gdp_data = await get_gdp_data("2023:4")
        >>> print(f"Number of observations: {len(gdp_data.observations)}")
    """
    return await get_forecast_data("GDP", policy_round)

async def get_unemployment_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's unemployment rate (seasonally adjusted).

    Fetches forecast data for the unemployment rate in Sweden, with seasonal adjustments.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing unemployment rate data.
        
    Example:
        >>> unemployment = await get_unemployment_data()
        >>> latest = unemployment.observations[-1] if unemployment.observations else None
        >>> if latest:
        >>>     print(f"Latest unemployment rate: {latest.value}%")
    """
    series_id = "SEQLABUEASA"  # Unemployment rate series ID
    return await get_forecast_data(series_id, policy_round)

async def get_cpi_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's Consumer Price Index (CPI) data.

    Fetches forecast data for the Consumer Price Index in Sweden.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing CPI data.
    """
    series_id = "SECPIYRCA"  # CPI series ID
    return await get_forecast_data(series_id, policy_round)

async def get_cpif_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's CPIF (Consumer Price Index with Fixed Interest Rate) data.

    Fetches forecast data for the CPIF in Sweden, which measures inflation with
    fixed mortgage rates.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing CPIF data.
    """
    series_id = "SECPIFYRCA"  # CPIF series ID
    return await get_forecast_data(series_id, policy_round)

async def get_cpif_ex_energy_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's CPIF excluding energy data.

    Fetches forecast data for the CPIF excluding energy prices in Sweden.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing CPIF excluding energy data.
    """
    series_id = "SECPIFXEYRCA"  # CPIF excluding energy series ID
    return await get_forecast_data(series_id, policy_round)

async def get_hourly_labour_cost_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's hourly labour cost data.

    Fetches forecast data for hourly labour costs in Sweden.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing hourly labour cost data.
    """
    series_id = "SEHLCYRCA"  # Hourly labour cost series ID
    return await get_forecast_data(series_id, policy_round)

async def get_hourly_wage_na_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's hourly wage (National Accounts) data.

    Fetches forecast data for hourly wages according to National Accounts.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing hourly wage data.
    """
    series_id = "SEHWNAYRCA"  # Hourly wage (NA) series ID
    return await get_forecast_data(series_id, policy_round)

async def get_hourly_wage_nmo_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's hourly wage (National Mediation Office) data.

    Fetches forecast data for hourly wages according to the National Mediation Office.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing hourly wage data.
    """
    series_id = "SEHWNMOYRCA"  # Hourly wage (NMO) series ID
    return await get_forecast_data(series_id, policy_round)

async def get_nominal_exchange_rate_kix_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's nominal exchange rate (KIX) data.

    Fetches forecast data for the KIX (krona index) nominal exchange rate.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing KIX exchange rate data.
    """
    series_id = "SEKIXYRCA"  # KIX exchange rate series ID
    return await get_forecast_data(series_id, policy_round)

async def get_population_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve Sweden's population data.

    Fetches forecast data for Sweden's population.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing population data.
    """
    series_id = "SEPOPYRCA"  # Population series ID
    return await get_forecast_data(series_id, policy_round)

async def get_employed_persons_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve data on employed persons in Sweden.

    Fetches forecast data for the number of employed persons in Sweden.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing employment data.
    """
    series_id = "SEEMPYRCA"  # Employed persons series ID
    return await get_forecast_data(series_id, policy_round)

async def get_labour_force_data(policy_round: Optional[str] = None) -> ForecastResult:
    """
    Retrieve data on the labour force in Sweden.

    Fetches forecast data for the size of the labour force in Sweden.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g. "2023:4").

    Returns:
        ForecastResult: A validated model containing labour force data.
    """
    series_id = "SELABFYRCA"  # Labour force series ID
    return await get_forecast_data(series_id, policy_round)
