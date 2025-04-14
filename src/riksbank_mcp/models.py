"""
Pydantic models for Riksbank data validation and documentation.
"""

from datetime import date

from pydantic import BaseModel, Field


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


class CalendarDay(BaseModel):
    """
    Represents a single calendar date and its properties, as per the
    SWEA API /CalendarDays endpoints.
    """

    calendar_date: date = Field(..., alias="calendarDate")
    swedish_bankday: bool = Field(..., alias="swedishBankday")
    week_year: int = Field(..., alias="weekYear")
    week_number: int = Field(..., alias="weekNumber")
    quarter_number: int = Field(..., alias="quarterNumber")
    ultimo: bool


class CrossRate(BaseModel):
    """
    Represents a single cross-rate observation, as returned by
    the SWEA API /CrossRates endpoints.
    """

    date: date
    value: float


class CrossRateAggregate(BaseModel):
    """
    Represents an aggregated cross-rate observation (e.g. monthly, quarterly),
    as returned by the SWEA API /CrossRateAggregates endpoints.
    """

    year: int
    seqNr: int
    value: float
