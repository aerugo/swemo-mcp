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
    cut = base.metadata.forecast_cutoff_date
    tail: list[ForecastObservation] = [
        o
        for o in latest.observations
        if (not o.is_forecast) and (date.fromisoformat(o.dt) > cut)
    ]
    seen = {o.dt for o in base.observations}
    combined = list(chain(base.observations, (o for o in tail if o.dt not in seen)))
    return base.model_copy(update={"observations": combined})


@runtime_checkable
class SeriesFetcher(Protocol):
    async def __call__(
        self, series_id: str, policy_round: str | None
    ) -> MonetaryPolicyDataResponse: ...
