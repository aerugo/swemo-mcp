"""
Pydantic models for Riksbank data validation and documentation.
"""

from pydantic import BaseModel


class Observation(BaseModel):
    """
    A single observation of an economic indicator.
    """

    date: str
    value: float


class ForecastResult(BaseModel):
    """
    Result of a forecast data query.
    """

    series_id: str
    policy_round: str | None = None
    observations: list[Observation]


class PolicyRound(BaseModel):
    """
    Information about a monetary policy round.
    """

    id: str
    date: str
    description: str | None = None


class SeriesInfo(BaseModel):
    """
    Information about an economic data series.
    """

    id: str
    name: str
    description: str | None = None
    unit: str | None = None


class ExchangeRateData(BaseModel):
    """
    Exchange rate data result.
    """

    series_id: str
    observations: list[Observation]


class InterestRateData(BaseModel):
    """
    Interest rate data result.
    """

    observations: list[Observation]
