"""
Pydantic models for Riksbank data validation and documentation.
"""
from typing import List, Optional, Any
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
    policy_round: Optional[str] = None
    observations: List[Observation]


class PolicyRound(BaseModel):
    """
    Information about a monetary policy round.
    """
    id: str
    date: str
    description: Optional[str] = None


class SeriesInfo(BaseModel):
    """
    Information about an economic data series.
    """
    id: str
    name: str
    description: Optional[str] = None
    unit: Optional[str] = None


class ExchangeRateData(BaseModel):
    """
    Exchange rate data result.
    """
    series_id: str
    observations: List[Observation]


class InterestRateData(BaseModel):
    """
    Interest rate data result.
    """
    observations: List[Observation]
