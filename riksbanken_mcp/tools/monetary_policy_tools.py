"""
Tools for working with the Riksbank's Monetary Policy data.
"""

from riksbanken_mcp.models import ForecastResult, Observation, PolicyRound, SeriesInfo
from riksbanken_mcp.services.monetary_policy_api import riksbanken_request


async def list_policy_rounds() -> list[PolicyRound]:
    """
    List all available monetary policy rounds from the Riksbank.

    Retrieves a comprehensive list of all monetary policy rounds, including their
    identifiers, dates, and descriptions when available.

    Returns:
        list[PolicyRound]: A list of policy rounds with their metadata.

    Example:
        >>> rounds = await list_policy_rounds()
        >>> for r in rounds:
        >>>     print(f"{r.id}: {r.date}")
    """
    response = await riksbanken_request("policy-rounds")
    rounds_data = response["policyRounds"]

    return [
        PolicyRound(
            id=round_data.get("id", ""),
            date=round_data.get("date", ""),
            description=round_data.get("description", None),
        )
        for round_data in rounds_data
    ]


async def list_series_ids() -> list[SeriesInfo]:
    """
    List all available series IDs for forecasts from the Riksbank.

    Retrieves metadata about all economic data series available through the
    Monetary Policy API, including identifiers, names, and descriptions.

    Returns:
        list[SeriesInfo]: A list of series information objects with metadata.

    Example:
        >>> series_list = await list_series_ids()
        >>> for series in series_list:
        >>>     print(f"{series.id}: {series.name}")
    """
    response = await riksbanken_request("series")
    series_data = response["series"]

    return [
        SeriesInfo(
            id=series.get("id", ""),
            name=series.get("name", ""),
            description=series.get("description", None),
            unit=series.get("unit", None),
        )
        for series in series_data
    ]


async def get_forecast_data(
    series_id: str, policy_round: str | None = None
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
        >>>     print(f"{obs.date}: {obs.value}")
    """
    params = {"seriesid": series_id}
    if policy_round:
        params["policyround"] = policy_round

    response = await riksbanken_request("forecasts", params)
    raw_items = response.get("forecasts", [])
    observations: list[Observation] = []

    for item in raw_items:
        # Convert API response to Observation model
        observations.append(
            Observation(
                date=item.get("date", item.get("dt", "")),
                value=float(item.get("value", item.get("val", 0.0))),
            )
        )

    return ForecastResult(
        series_id=series_id, policy_round=policy_round, observations=observations
    )


async def get_gdp_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's Gross Domestic Product (GDP).

    GDP is a key economic indicator representing the total output of goods and services
    within the country. This series is typically reported on a quarterly or annual basis,
    though forecast data may be available at additional frequencies according to Riksbank's methodology.

    Args:
        policy_round (Optional[str]): If provided, filters forecasts to a specific monetary
            policy publication cycle (e.g., "2024:1"). If omitted, data for all available rounds is returned.

    Returns:
        ForecastResult: A Pydantic model containing:
          - `series_id`: "GDP"
          - `policy_round`: The specified round or None
          - `observations`: A list of (date, value) pairs representing GDP forecast (in billion SEK).

    Usage Example:
        >>> gdp_forecast = await get_gdp_data("2023:4")
        >>> for obs in gdp_forecast.observations:
        ...     print(f"Date: {obs.date}, GDP forecast: {obs.value} (billion SEK)")

    Interpretation:
        - Positive growth suggests an expanding economy.
        - Negative or slowing growth may indicate economic contraction.

    Disclaimer:
        Forecasts are subject to revision and should be compared with other institutions' estimates.
    """
    return await get_forecast_data("GDP", policy_round)


async def get_unemployment_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's unemployment rate (seasonally adjusted).

    The unemployment rate indicates the percentage of the labor force that is unemployed
    while actively seeking work. It is a critical measure for assessing labor market conditions.

    Args:
        policy_round (Optional[str]): If provided, returns data for the specified monetary
            policy round; otherwise, data from all rounds is returned.

    Returns:
        ForecastResult: A validated model containing unemployment rate forecasts.

    Usage Example:
        >>> unemployment_forecast = await get_unemployment_data("2023:4")
        >>> print("Latest rate:", unemployment_forecast.observations[-1].value)

    Data Frequency & Range:
        - Typically reported monthly or quarterly.
        - Values historically range between 2% and 20%, though extreme conditions can cause deviations.

    Interpretation:
        - Rising rates may flag economic downturns.
        - Falling rates suggest labor market tightening.

    Disclaimer:
        Forecasts assume stable macro conditions. Unexpected shocks can lead to significant deviations.
    """
    series_id = "SEQLABUEASA"  # Unemployment rate series ID
    return await get_forecast_data(series_id, policy_round)


async def get_cpi_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's Consumer Price Index (CPI).

    CPI measures the average change in prices over time of a basket of consumer goods and services.
    It is a primary indicator of inflation used in monetary policy decisions.

    Args:
        policy_round (Optional[str]): Filters data to a specific policy round if provided.

    Returns:
        ForecastResult: A Pydantic model containing forecasted CPI data (typically annual percentage changes).

    Usage Example:
        >>> cpi_forecast = await get_cpi_data("2024:1")
        >>> for obs in cpi_forecast.observations:
        ...     print(f"{obs.date}: {obs.value}% inflation")

    Data Frequency & Range:
        - Often reported monthly or quarterly; forecasts may be quarterly or annual.
        - Annual inflation generally ranges from -1% to +10% in stable economies.

    Interpretation:
        - Rising CPI suggests increasing consumer prices.
        - Deflation or very low inflation may trigger expansionary policy.

    Disclaimer:
        Methodological differences exist among institutions; compare with external data for consistency.
    """
    series_id = "SECPIYRCA"  # CPI series ID
    return await get_forecast_data(series_id, policy_round)


async def get_cpif_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve Sweden's CPIF (Consumer Price Index with Fixed Interest Rate) forecast.

    CPIF holds mortgage interest expenditure constant to provide a stable view of core inflation.
    It is widely used by the Riksbank for underlying inflation analysis.

    Args:
        policy_round (Optional[str]): Monetary policy round identifier.

    Returns:
        ForecastResult: A validated model containing CPIF forecast data.

    Usage Example:
        >>> cpif_data = await get_cpif_data()
        >>> print("CPIF forecast sample:", cpif_data.observations[:5])

    Frequency & Notes:
        - Measured monthly or quarterly; compare with headline CPI to assess interest rate impacts.

    Disclaimer:
        CPIF is specific to the Swedish context and should be interpreted alongside other inflation measures.
    """
    series_id = "SECPIFYRCA"  # CPIF series ID
    return await get_forecast_data(series_id, policy_round)


async def get_cpif_ex_energy_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve Sweden's CPIF excluding energy forecast data.

    This metric refines CPIF by eliminating the volatility due to energy prices,
    offering a clearer view of underlying inflation trends.

    Args:
        policy_round (Optional[str]): Filter forecasts to a specific round if provided.

    Returns:
        ForecastResult: A validated model of CPIF ex-energy forecast data.

    Usage Example:
        >>> cpif_xe = await get_cpif_ex_energy_data("2023:4")
        >>> for obs in cpif_xe.observations:
        ...     print(f"{obs.date}: {obs.value}%")

    Interpretation:
        - Provides a smoother inflation trend by excluding energy's inherent volatility.

    Disclaimer:
        Excluding energy may omit key influences in periods where energy costs drive broader inflation.
    """
    series_id = "SECPIFXEYRCA"  # CPIF excluding energy series ID
    return await get_forecast_data(series_id, policy_round)


async def get_hourly_labour_cost_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's hourly labour cost.

    This series, which includes wages plus employer contributions, is crucial for analyzing cost-push
    inflation and business profit margins.

    Args:
        policy_round (Optional[str]): If provided, returns data from the specified policy round.

    Returns:
        ForecastResult: A validated model containing forecast data for hourly labour costs.

    Usage Example:
        >>> labour_costs = await get_hourly_labour_cost_data("2023:3")
        >>> print(labour_costs.observations[0].value, "SEK per hour")

    Frequency & Range:
        - Typically aggregated quarterly or annually. Annual changes may range from ~1% to ~5%.

    Disclaimer:
        Aggregate figures may obscure sector-specific variations. Detailed analysis may require disaggregated data.
    """
    series_id = "SEHLCYRCA"  # Hourly labour cost series ID
    return await get_forecast_data(series_id, policy_round)


async def get_hourly_wage_na_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's hourly wage (National Accounts).

    This metric represents gross wages per hour based on national accounts data and is used to assess
    trends in labor costs and potential inflationary pressures.

    Args:
        policy_round (Optional[str]): Specific monetary policy round to filter the data.

    Returns:
        ForecastResult: A validated model containing hourly wage NA forecast data.

    Usage Example:
        >>> wages_na = await get_hourly_wage_na_data()
        >>> for obs in wages_na.observations:
        ...     print(f"Wage on {obs.date}: {obs.value} SEK/hour (NA)")

    Interpretation:
        - Strong wage growth may signal inflationary pressures.
        - Weak wage growth may suggest subdued consumer spending.

    Disclaimer:
        National Accounts data may smooth out short-term variations. Cross-reference with sector-specific data if needed.
    """
    series_id = "SEHWNAYRCA"  # Hourly wage (NA) series ID
    return await get_forecast_data(series_id, policy_round)


async def get_hourly_wage_nmo_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's hourly wage (National Mediation Office).

    This measure, based on data collected for collective bargaining, offers an alternate view of wage trends.

    Args:
        policy_round (Optional[str]): If specified, filters data to the desired policy round.

    Returns:
        ForecastResult: A validated model containing NMO-based hourly wage forecasts.

    Usage Example:
        >>> wages_nmo = await get_hourly_wage_nmo_data("2023:2")
        >>> latest = wages_nmo.observations[-1]
        >>> print(f"NMO wage: {latest.value} SEK/hour")

    Frequency & Range:
        - Commonly reported monthly or quarterly. Fluctuations may vary by industry.

    Disclaimer:
        NMO figures may omit irregular bonuses or non-wage compensations. For comprehensive wage trends, compare multiple sources.
    """
    series_id = "SEHWNMOYRCA"  # Hourly wage (NMO) series ID
    return await get_forecast_data(series_id, policy_round)


async def get_nominal_exchange_rate_kix_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's nominal exchange rate (KIX).

    KIX measures the value of the krona against a trade-weighted basket of major currencies.
    It is used to assess international competitiveness and potential effects on exports.

    Args:
        policy_round (Optional[str]): Optional policy round identifier (e.g., "2024:1").

    Returns:
        ForecastResult: A validated model containing KIX exchange rate forecasts.

    Usage Example:
        >>> kix_data = await get_nominal_exchange_rate_kix_data()
        >>> print(kix_data.observations[:3])

    Frequency & Interpretation:
        - Typically updated daily or monthly. Higher KIX values indicate a stronger krona.

    Disclaimer:
        Exchange rates are volatile. This forecast is one scenario among many.
    """
    series_id = "SEKIXYRCA"  # KIX exchange rate series ID
    return await get_forecast_data(series_id, policy_round)


async def get_population_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for Sweden's population.

    Population data provides context for labor market trends, economic demand, and long-term planning.

    Args:
        policy_round (Optional[str]): Optional filter for a specific forecast cycle.

    Returns:
        ForecastResult: A validated model containing population forecast data with (date, value) pairs.

    Usage Example:
        >>> pop_data = await get_population_data("2025:1")
        >>> print(pop_data.observations[-1].value, "forecasted population")

    Disclaimer:
        Demographic forecasts are sensitive to migration and birth rate assumptions. Always consult official statistics for verification.
    """
    series_id = "SEPOPYRCA"  # Population series ID
    return await get_forecast_data(series_id, policy_round)


async def get_employed_persons_data(
    policy_round: str | None = None,
) -> ForecastResult:
    """
    Retrieve forecast data for the total number of employed persons in Sweden.

    This data reflects the aggregate number of people in paid employment, serving as an important proxy
    for labor market health.

    Args:
        policy_round (Optional[str]): If provided, returns data from the specified policy round.

    Returns:
        ForecastResult: A validated model containing employment forecast data.

    Usage Example:
        >>> employed_data = await get_employed_persons_data("2024:2")
        >>> for obs in employed_data.observations:
        ...     print(f"{obs.date}: {obs.value} employed")

    Interpretation:
        - Growth indicates a healthy, expanding labor market.
        - Declines may signal economic downturns or structural changes.

    Disclaimer:
        This aggregate does not differentiate between full-time and part-time employment.
    """
    series_id = "SEEMPYRCA"  # Employed persons series ID
    return await get_forecast_data(series_id, policy_round)


async def get_labour_force_data(policy_round: str | None = None) -> ForecastResult:
    """
    Retrieve forecast data for the size of the Swedish labour force.

    The labour force measures all individuals of working age who are employed or actively seeking work.
    It is essential for understanding long-term economic and labor market trends.

    Args:
        policy_round (Optional[str]): Filter for a specific forecast cycle if desired.

    Returns:
        ForecastResult: A validated model containing labour force forecast data.

    Usage Example:
        >>> labor_force = await get_labour_force_data()
        >>> print("Latest forecasted labour force:", labor_force.observations[-1].value)

    Interpretation:
        - Increases signal a growing pool of potential workers, which could moderate wage pressures.
        - Decreases may indicate demographic shifts or reduced participation.

    Disclaimer:
        Aggregate figures do not capture detailed demographic breakdowns; further analysis may be required.
    """
    series_id = "SELABFYRCA"  # Labour force series ID
    return await get_forecast_data(series_id, policy_round)
