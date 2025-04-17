"""
Pydantic models for Riksbank data validation and documentation.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class Observation(BaseModel):
    """
    A single observation of an economic indicator.
    """

    date: str
    value: float


class ForecastMetadata(BaseModel):
    """
    Metadata for a forecast vintage.
    """

    revision_dtm: datetime | None = Field(
        None,
        description="Timestamp when this forecast was revised (may be missing)",
    )
    forecast_cutoff_date: date = Field(
        ..., description="Date when forecast data was finalized"
    )
    policy_round: str = Field(
        ..., description="Policy round identifier (e.g. '2023:4')"
    )
    policy_round_code: str | None = Field(
        None,
        description="Internal code for the policy round (may be missing)",
    )
    policy_round_end_dtm: datetime = Field(
        ..., description="End timestamp for the policy round"
    )


class ForecastObservation(BaseModel):
    """
    A single forecast observation with date and value.
    """

    dt: str = Field(
        ..., description="Date of the forecasted observation in YYYY-MM-DD format"
    )
    value: float = Field(..., description="Value of the forecasted observation")


class ForecastVintage(BaseModel):
    """
    A forecast vintage containing metadata and observations.
    """

    metadata: ForecastMetadata
    observations: list[ForecastObservation]


class ForecastSeries(BaseModel):
    """
    A complete forecast series with its vintages.
    """

    external_id: str = Field(..., description="Series identifier")
    vintages: list[ForecastVintage]


class ForecastResult(BaseModel):
    """
    Result of a forecast data query.
    """

    series_id: str
    policy_round: str
    observations: list[Observation]


class PolicyRound(BaseModel):
    """
    Information about a monetary policy round.
    """

    id: str
    year: int
    iteration: int


class SeriesInfo(BaseModel):
    """
    Information about an economic data series.
    """

    id: str
    decimals: int
    start_date: date
    description: str
    source_agency: str
    unit: str
    note: str | None = None


class MonetaryPolicyDataResponse(BaseModel):
    """
    Represents the response from the Monetary Policy Data endpoint main endpoint.
    """

    external_id: str
    vintages: list[ForecastVintage]


class MonetaryPolicyDataRoundsResponse(BaseModel):
    """
    Represents the response from the Monetary Policy Data endpoint for rounds.
    """

    rounds: list[PolicyRound]


class MonetaryPolicyDataSeriesResponse(BaseModel):
    """
    Represents the response from the Monetary Policy Data endpoint for series.
    """

    series: list[SeriesInfo]
