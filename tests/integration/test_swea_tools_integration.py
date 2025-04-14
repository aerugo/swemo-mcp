import pytest
from datetime import date

from riksbank_mcp.models import (
    Observation,
    CalendarDay,
    CrossRate,
    CrossRateAggregate,
    InterestRateData,
    ExchangeRateData,
)
from riksbank_mcp.tools import swea_tools

# You may add a marker for integration tests, e.g.:
pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_fetch_observations():
    # Using a known series ID – adjust as necessary.
    # Here we use "SEKUSDPMI" shown in get_usd_exchange_rate.
    series_id = "SEKUSDPMI"
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    obs = await swea_tools.fetch_observations(series_id, from_date_val, to_date_val)
    assert isinstance(obs, list)
    # If data is returned, check the structure
    if obs:
        first = obs[0]
        assert isinstance(first, Observation)
        assert first.date != ""
        assert isinstance(first.value, float)


@pytest.mark.asyncio
async def test_get_latest_observation():
    # Use a known series for latest observation
    series_id = "SEKUSDPMI"
    latest = await swea_tools.get_latest_observation(series_id)
    # May return None if no data is available
    if latest is not None:
        assert isinstance(latest, Observation)
        assert latest.date != ""
        assert latest.value > 0


@pytest.mark.asyncio
async def test_get_policy_rate():
    # Test the get_policy_rate which uses a fixed series ID ("SE0001")
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 3, 1)
    result: InterestRateData = await swea_tools.get_policy_rate(from_date_val, to_date_val)
    assert isinstance(result, InterestRateData)
    # If observations are available, validate the first one
    if result.observations:
        first = result.observations[0]
        assert isinstance(first, Observation)
        assert first.date != ""


@pytest.mark.asyncio
async def test_get_usd_exchange_rate():
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    result: ExchangeRateData = await swea_tools.get_usd_exchange_rate(from_date_val, to_date_val)
    assert isinstance(result, ExchangeRateData)
    # The series id should match what the function sets
    assert result.series_id == "SEKUSDPMI"
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""


@pytest.mark.asyncio
async def test_get_eur_exchange_rate():
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    result: ExchangeRateData = await swea_tools.get_eur_exchange_rate(from_date_val, to_date_val)
    assert isinstance(result, ExchangeRateData)
    assert result.series_id == "SEKEURPMI"
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""


@pytest.mark.asyncio
async def test_get_gbp_exchange_rate():
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 31)
    result: ExchangeRateData = await swea_tools.get_gbp_exchange_rate(from_date_val, to_date_val)
    assert isinstance(result, ExchangeRateData)
    assert result.series_id == "SEKGBPPMI"
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""


@pytest.mark.asyncio
async def test_get_mortgage_rate():
    from_date_val = date(2022, 1, 1)
    to_date_val = date(2022, 12, 31)
    result = await swea_tools.get_mortgage_rate(from_date_val, to_date_val)
    assert isinstance(result, InterestRateData)
    if result.observations:
        obs = result.observations[0]
        assert isinstance(obs, Observation)
        assert obs.date != ""


@pytest.mark.asyncio
async def test_get_calendar_days():
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 15)
    days = await swea_tools.get_calendar_days(from_date_val, to_date_val)
    assert isinstance(days, list)
    if days:
        day = days[0]
        assert isinstance(day, CalendarDay)
        assert day.calendar_date is not None


@pytest.mark.asyncio
async def test_get_cross_rates():
    # Use two known series for cross rates
    series_id1 = "SEKUSDPMI"
    series_id2 = "SEKEURPMI"
    from_date_val = date(2023, 1, 1)
    to_date_val = date(2023, 1, 15)
    cross_rates = await swea_tools.get_cross_rates(series_id1, series_id2, from_date_val, to_date_val)
    assert isinstance(cross_rates, list)
    if cross_rates:
        rate = cross_rates[0]
        assert isinstance(rate, CrossRate)
        assert rate.date != ""


@pytest.mark.asyncio
async def test_get_cross_rate_aggregates():
    series_id1 = "SEKUSDPMI"
    series_id2 = "SEKEURPMI"
    from_date_val = date(2023, 1, 1)
    # Test with monthly aggregate ("M") over a couple of months
    aggregates = await swea_tools.get_cross_rate_aggregates(series_id1, series_id2, "M", from_date_val, date(2023, 3, 1))
    assert isinstance(aggregates, list)
    if aggregates:
        agg = aggregates[0]
        assert isinstance(agg, CrossRateAggregate)
        # Assert that the year is a positive integer
        assert agg.year > 0


@pytest.mark.asyncio
async def test_list_groups():
    groups = await swea_tools.list_groups("en")
    assert isinstance(groups, dict)
    # Optionally, check that some expected key exists if known


@pytest.mark.asyncio
async def test_get_group_details():
    # Use a group id that is likely to exist; adjust if known.
    details = await swea_tools.get_group_details(130, "en")
    assert isinstance(details, dict)
    if "name" in details:
        assert details["name"] != ""


@pytest.mark.asyncio
async def test_list_series():
    series_list = await swea_tools.list_series("en")
    assert isinstance(series_list, list)
    if series_list:
        first = series_list[0]
        assert isinstance(first, dict)
        assert "seriesId" in first


@pytest.mark.asyncio
async def test_get_series_info():
    series_list = await swea_tools.list_series("en")
    if series_list:
        series_id = series_list[0].get("seriesId")
        info = await swea_tools.get_series_info(series_id, "en")
        if info is not None:
            assert isinstance(info, dict)
            assert info.get("seriesId") == series_id


@pytest.mark.asyncio
async def test_list_exchange_rate_series():
    fx_series = await swea_tools.list_exchange_rate_series("en")
    assert isinstance(fx_series, list)
    if fx_series:
        first = fx_series[0]
        assert isinstance(first, dict)
        assert "seriesId" in first
