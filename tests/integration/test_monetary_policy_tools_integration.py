import pytest
from datetime import date

from riksbank_mcp.models import ForecastResult, PolicyRound, SeriesInfo, Observation
from riksbank_mcp.tools import monetary_policy_tools as mpt

pytestmark = pytest.mark.integration

@pytest.mark.asyncio
async def test_list_policy_rounds():
    rounds = await mpt.list_policy_rounds()
    assert isinstance(rounds, list)
    if rounds:
        first = rounds[0]
        assert isinstance(first, PolicyRound)
        assert first.id != ""
        assert first.date != ""

@pytest.mark.asyncio
async def test_list_series_ids():
    series_list = await mpt.list_series_ids()
    assert isinstance(series_list, list)
    if series_list:
        first = series_list[0]
        assert isinstance(first, SeriesInfo)
        assert first.id != ""
        assert first.name != ""

@pytest.mark.asyncio
async def test_get_forecast_data_without_policy_round():
    # Use a known series ID that should return forecast data; adjust as needed.
    series_id = "SEQGDPNAYCA"  # Example: GDP year-over-year growth
    result: ForecastResult = await mpt.get_forecast_data(series_id)
    assert isinstance(result, ForecastResult)
    assert result.series_id == series_id
    # Observations might be empty if no data is present; if not, verify one observation.
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""
        assert isinstance(first_obs.value, float)

@pytest.mark.asyncio
async def test_get_forecast_data_with_policy_round():
    series_id = "SEQGDPNAYCA"  # GDP series example
    policy_round = "2023:4"   # Adjust as per known available rounds
    result: ForecastResult = await mpt.get_forecast_data(series_id, policy_round)
    assert isinstance(result, ForecastResult)
    assert result.series_id == series_id
    # If observations are returned, check the first one
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_gdp_data():
    result: ForecastResult = await mpt.get_gdp_data()
    assert isinstance(result, ForecastResult)
    # If observations exist, at least one record should have a non-empty date.
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_unemployment_data():
    result: ForecastResult = await mpt.get_unemployment_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_cpi_data():
    result: ForecastResult = await mpt.get_cpi_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_cpif_data():
    result: ForecastResult = await mpt.get_cpif_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_cpif_ex_energy_data():
    result: ForecastResult = await mpt.get_cpif_ex_energy_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_hourly_labour_cost_data():
    result: ForecastResult = await mpt.get_hourly_labour_cost_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        first_obs = result.observations[0]
        assert isinstance(first_obs, Observation)
        assert first_obs.date != ""

@pytest.mark.asyncio
async def test_get_hourly_wage_na_data():
    result: ForecastResult = await mpt.get_hourly_wage_na_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_hourly_wage_nmo_data():
    result: ForecastResult = await mpt.get_hourly_wage_nmo_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_nominal_exchange_rate_kix_data():
    result: ForecastResult = await mpt.get_nominal_exchange_rate_kix_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_population_data():
    result: ForecastResult = await mpt.get_population_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_employed_persons_data():
    result: ForecastResult = await mpt.get_employed_persons_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_labour_force_data():
    result: ForecastResult = await mpt.get_labour_force_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

# Additional Interesting Series

@pytest.mark.asyncio
async def test_get_gdp_gap_data():
    result: ForecastResult = await mpt.get_gdp_gap_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_policy_rate_data():
    result: ForecastResult = await mpt.get_policy_rate_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        # Use last observation if available
        obs = result.observations[-1]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_general_government_net_lending_data():
    result: ForecastResult = await mpt.get_general_government_net_lending_data()
    assert isinstance(result, ForecastResult)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""
