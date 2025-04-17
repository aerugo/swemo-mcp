from __future__ import annotations

from itertools import chain
from typing import Protocol, runtime_checkable

from riksbank_mcp.models import (
    ForecastObservation,
    ForecastVintage,
    MonetaryPolicyDataResponse,
)


def merge_realized(base: ForecastVintage, latest: ForecastVintage) -> ForecastVintage:
    """
    Keep every original observation (history + forecasts) and add a
    `realized` companion value.

    • For each *forecast* in the base vintage, try to pull the realised
      outcome of the same date from the latest vintage.
    • For historical observations, `realized` simply repeats `value`.
    • Realised observations that are **not** present in the base vintage
      (because the date lay beyond the original cut‑off) are appended as
      separate rows (is_forecast == False).
    """
    # ---------- map date → realised value from the latest vintage ----------
    realized_map: dict[str, float] = {
        o.dt: o.value for o in latest.observations if not o.is_forecast
    }

    # ---------- enrich every base observation ----------
    enriched_base: list[ForecastObservation] = []
    for obs in base.observations:
        realized_val = realized_map.get(obs.dt) if obs.is_forecast else obs.value
        enriched_base.append(
            ForecastObservation.model_validate(
                {
                    "dt": obs.dt,
                    "value": obs.value,
                    "is_forecast": obs.is_forecast,
                    "realized": realized_val,
                }
            )
        )

    # ---------- add realised observations missing from base ----------
    base_dates = {o.dt for o in base.observations}
    extra_realized: list[ForecastObservation] = [
        ForecastObservation.model_validate(
            {
                "dt": o.dt,
                "value": o.value,
                "is_forecast": False,
                "realized": o.value,
            }
        )
        for o in latest.observations
        if (not o.is_forecast) and (o.dt not in base_dates)
    ]

    # ---------- combine & sort chronologically ----------
    combined = sorted(chain(enriched_base, extra_realized), key=lambda o: o.dt)

    return base.model_copy(update={"observations": list(combined)})


@runtime_checkable
class SeriesFetcher(Protocol):
    async def __call__(
        self, series_id: str, policy_round: str | None
    ) -> MonetaryPolicyDataResponse: ...
