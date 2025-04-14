import pytest
from datetime import date

from riksbank_mcp.models import Observation, InterestRateData
from riksbank_mcp.tools import swestr_tools as st

pytestmark = pytest.mark.integration

@pytest.mark.asyncio
async def test_fetch_interest_rate():
    # Test the low-level fetch function. Provide a recent interval.
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 10)
    # fetch_interest_rate returns a list[Observation] from the "rates" endpoint
    obs_list = await st.fetch_interest_rate(from_date_val, to_date_val)
    assert isinstance(obs_list, list)
    if obs_list:
        first = obs_list[0]
        assert isinstance(first, Observation)
        assert first.date != ""
        assert isinstance(first.value, float)

@pytest.mark.asyncio
async def test_get_swestr():
    # Test the get_swestr function, which simply wraps fetch_interest_rate and returns InterestRateData.
    from_date_val = date(2023, 1, 1)
    # You may provide an end date or leave it None to fetch up to the latest available data.
    result: InterestRateData = await st.get_swestr(from_date_val)
    assert isinstance(result, InterestRateData)
    # If observations are returned, check the first one.
    if result.observations:
        first = result.observations[0]
        assert isinstance(first, Observation)
        assert first.date != ""

@pytest.mark.asyncio
async def test_get_latest_swestr():
    # Test retrieval of the latest SWESTR observation.
    latest_obs = await st.get_latest_swestr()
    # The live API may return None if no data is yet available today. Otherwise,
    if latest_obs is not None:
        assert isinstance(latest_obs, Observation)
        assert latest_obs.date != ""
        assert isinstance(latest_obs.value, float)

@pytest.mark.asyncio
async def test_get_swestr_averages():
    # Test the averaged SWESTR time series.
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    result: InterestRateData = await st.get_swestr_averages(from_date_val, to_date_val)
    assert isinstance(result, InterestRateData)
    if result.observations:
        first = result.observations[0]
        assert isinstance(first, Observation)
        assert first.date != ""

@pytest.mark.asyncio
async def test_get_swestr_1week():
    # Test the 1-week SWESTR average.
    # Provide a date range where data is available.
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    result: InterestRateData = await st.get_swestr_1week(from_date_val, to_date_val)
    assert isinstance(result, InterestRateData)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""

@pytest.mark.asyncio
async def test_get_swestr_1month():
    # Test the 1-month SWESTR average.
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    result: InterestRateData = await st.get_swestr_1month(from_date_val, to_date_val)
    assert isinstance(result, InterestRateData)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""
