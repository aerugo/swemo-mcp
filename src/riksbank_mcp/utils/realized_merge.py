from __future__ import annotations

from datetime import date
from itertools import chain
from typing import Protocol, runtime_checkable

from riksbank_mcp.models import (
    ForecastObservation,
    ForecastVintage,
    MonetaryPolicyDataResponse,
)


def merge_realized(base: ForecastVintage, latest: ForecastVintage) -> ForecastVintage:
    """
    Enrich `base` so that every forecast row also carries its realised value
    (if now known) **without discarding the original forecast**.
    """
    cut = base.metadata.forecast_cutoff_date

    # map date → realised outcome from latest vintage (only observational rows)
    realized_map: dict[str, float] = {
        o.dt: o.value
        for o in latest.observations
        if (o.observation is not None) and (date.fromisoformat(o.dt) > cut)
    }

    enriched: list[ForecastObservation] = []
    for o in base.observations:
        realized_val = (
            realized_map.get(o.dt) if o.forecast is not None else o.value
        )
        enriched.append(
            ForecastObservation.model_validate(
                {
                    "dt": o.dt,
                    "value": o.value,
                    "forecast": o.forecast,
                    "observation": o.observation,
                    "realized": realized_val,
                }
            )
        )

    # add observational rows that were absent from the base vintage
    base_dates = {o.dt for o in base.observations}
    tail: list[ForecastObservation] = [
        ForecastObservation.model_validate(
            {
                "dt": o.dt,
                "value": o.value,
                "forecast": None,
                "observation": o.value,
                "realized": o.value,
            }
        )
        for o in latest.observations
        if (o.observation is not None) and (o.dt not in base_dates)
    ]

    combined = sorted(chain(enriched, tail), key=lambda r: r.dt)
    return base.model_copy(update={"observations": combined})


@runtime_checkable
class SeriesFetcher(Protocol):
    async def __call__(
        self, series_id: str, policy_round: str | None
    ) -> MonetaryPolicyDataResponse: ...
