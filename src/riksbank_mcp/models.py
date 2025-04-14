"""
Pydantic models for Riksbank data validation and documentation.
"""

from __future__ import annotations

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

    class Config:
        allow_population_by_field_name = True


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

    year: int = Field(..., alias="Year")
    seqNr: int = Field(..., alias="SeqNr")
    value: float = Field(..., alias="Value")

    class Config:
        allow_population_by_field_name = True


class ObservationAggregate(BaseModel):
    """
    Represents an aggregated observation (e.g. weekly, monthly, quarterly, yearly)
    as returned by the SWEA API /ObservationAggregates endpoints.

    Fields:
        year (int): Calendar or fiscal year of this aggregate.
        seq_nr (int): Sequence index of the aggregate within the year (e.g., which week/quarter).
        from_date (str): Start date of the aggregated period, ISO 8601 (YYYY-MM-DD).
        to_date (str): End date of the aggregated period, ISO 8601 (YYYY-MM-DD).
        average (float): Average value across all underlying observations in the period.
        min (float): Minimum observed value in the period.
        max (float): Maximum observed value in the period.
        ultimo (float): The last valid observation in the period (e.g., last bank day).
        observation_count (int): Number of actual daily observations included in the aggregate.

    Usage:
        Use `get_observation_aggregates` for retrieving aggregated results directly from the SWEA API.
        Analysts can use these aggregates to monitor monthly, quarterly, or yearly trends in interest rates
        or exchange rates without manually summarizing daily observations.
    """

    year: int = Field(..., alias="year")
    seq_nr: int = Field(..., alias="seqNr")
    from_date: str = Field(..., alias="from")
    to_date: str = Field(..., alias="to")
    average: float
    min: float
    max: float
    ultimo: float
    observation_count: int = Field(..., alias="observationCount")

    class Config:
        allow_population_by_field_name = True
