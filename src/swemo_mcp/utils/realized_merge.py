from __future__ import annotations

from datetime import date
from itertools import chain
from typing import Protocol, runtime_checkable

from swemo_mcp.models import (
    ForecastObservation,
    ForecastVintage,
    MonetaryPolicyDataResponse,
)


def merge_realized(base: ForecastVintage, latest: ForecastVintage) -> ForecastVintage:
    """
    For every forecast row in *base*, copy the realised outcome from
    *latest* (if available) into the `observation` field – while keeping
    the original `forecast` value.  Also append observational rows that
    were not present in *base* yet.
    """
    cut = base.metadata.forecast_cutoff_date

    # map date → realised value from latest (observational rows only)
    obs_map: dict[str, float] = {
        o.dt: o.value
        for o in latest.observations
        if (o.observation is not None) and (date.fromisoformat(o.dt) > cut)
    }

    enriched: list[ForecastObservation] = []
    for o in base.observations:
        # If it's a forecast and a realised value exists, fill it
        obs_val = obs_map.get(o.dt) if o.forecast is not None else o.value
        enriched.append(
            ForecastObservation.model_validate(
                {
                    "dt": o.dt,
                    "value": o.value,
                    "forecast": o.forecast,
                    "observation": obs_val,
                }
            )
        )

    # Add observational rows missing from base
    base_dates = {o.dt for o in base.observations}
    tail = [
        ForecastObservation.model_validate(
            {
                "dt": o.dt,
                "value": o.value,
                "forecast": None,
                "observation": o.value,
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
