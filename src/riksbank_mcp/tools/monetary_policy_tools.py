"""
Riksbank Monetary‑Policy API helper functions
===========================================
"""

import logging
from datetime import date
from typing import Any

from riksbank_mcp.models import ForecastObservation  # NEW
from riksbank_mcp.models import (
    ForecastVintage,
    MonetaryPolicyDataResponse,
    MonetaryPolicyDataRoundsResponse,
    MonetaryPolicyDataSeriesResponse,
    PolicyRound,
    SeriesInfo,
)
from riksbank_mcp.query import ForecastRequest
from riksbank_mcp.services.monetary_policy_api import riksbanken_request
from riksbank_mcp.utils.realized_merge import SeriesFetcher, merge_realized

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# One‑liner shown to every LLM so it knows how to pass the argument.
# ---------------------------------------------------------------------

___all__ = [
    "list_policy_rounds",
    "list_series_ids",
    "get_policy_data",
    "get_gdp_data",
    "get_unemployment_data",
    "get_cpi_data",
    "get_cpif_data",
    "get_cpif_ex_energy_data",
    "get_hourly_labour_cost_data",
    "get_hourly_wage_na_data",
    "get_hourly_wage_nmo_data",
    "get_population_data",
    "get_employed_persons_data",
    "get_labour_force_data",
    "get_gdp_gap_data",
    "get_policy_rate_data",
    "get_general_government_net_lending_data",
    "get_gdp_level_saca_data",
    "get_gdp_level_ca_data",
    "get_gdp_level_na_data",
    "get_gdp_yoy_sa_data",
    "get_gdp_yoy_na_data",
    "get_cpi_index_data",
    "get_cpi_yoy_data",
    "get_cpif_yoy_data",
    "get_cpif_ex_energy_index_data",
    "get_nominal_exchange_rate_kix_index_data",
    "get_population_level_data",
]

# =============================================================================
# ─────────────────────────── Helper / discovery calls ─────────────────────────
# =============================================================================


async def list_policy_rounds() -> MonetaryPolicyDataRoundsResponse:
    """Return a catalogue of **monetary‑policy rounds** published by the Riksbank.

    A *policy round* designates a discrete set of forecasts typically
    released in either the **Monetary‑Policy Report (MPR)** or the shorter
    **Monetary‑Policy Update (MPU)**.  Identifiers follow the pattern
    ``YYYY:I``—for example ``2025:2`` for the second policy publication in
    2025.

    Example
    -------
    >>> rounds = await list_policy_rounds()
    >>> for r in rounds.rounds[:3]:
    ...     print(r.id, r.year, r.iteration)
    2025:2 2025 2
    2025:1 2025 1
    2024:3 2024 3

    Returns
    -------
    MonetaryPolicyDataRoundsResponse
        A pydantic model encapsulating a list of :class:`PolicyRound`
        objects (``rounds.rounds``).
    """
    payload: dict[str, Any] = await riksbanken_request("policy_rounds")
    identifiers: list[str] = payload.get("data", []) or []

    rounds: list[PolicyRound] = []
    for ident in identifiers:
        try:
            year_str, iter_str = ident.split(":")
            rounds.append(
                PolicyRound(
                    id=ident,
                    year=int(year_str),
                    iteration=int(iter_str),
                )
            )
        except ValueError:
            logger.warning(f"Unexpected policy round format: {ident}")

    return MonetaryPolicyDataRoundsResponse(rounds=rounds)


async def list_series_ids() -> MonetaryPolicyDataSeriesResponse:
    """List **all** series metadata available via the Monetary‑policy API.

    Use this when you need to discover *which* identifier corresponds to a
    particular economic concept.

    Returns
    -------
    MonetaryPolicyDataSeriesResponse
        Contains a list of :class:`SeriesInfo`—see attributes ``id``,
        ``description``, and so on.
    """
    payload: dict[str, Any] = await riksbanken_request("series_ids")
    entries: list[dict[str, Any]] = payload.get("data", []) or []

    series_list: list[SeriesInfo] = []
    for entry in entries:
        meta = entry.get("metadata", {})
        try:
            series_list.append(
                SeriesInfo(
                    id=entry.get("series_id", ""),
                    decimals=int(meta.get("decimals", 0)),
                    start_date=meta.get("start_date", ""),
                    description=meta.get("description", ""),
                    source_agency=meta.get("source_agency", ""),
                    unit=meta.get("unit", ""),
                    note=meta.get("note", None),
                )
            )
        except Exception as e:
            logger.error(
                f"Error parsing series metadata for {entry.get('series_id')}: {e}"
            )

    return MonetaryPolicyDataSeriesResponse(series=series_list)


# =============================================================================
# ────────────────────────── Generic data fetch wrapper ────────────────────────
# =============================================================================


async def get_policy_data(
    series_id: str, policy_round: str | None = None
) -> MonetaryPolicyDataResponse:
    """Low‑level fetcher for any *forecast* series.

    Parameters
    ----------
    series_id : str
        The Riksbank *series identifier* (e.g. ``"SEQGDPNAYCA"`` for GDP
        y/y growth, calendar‑adjusted).
    policy_round : str | None, default ``None``
        Optional filter such as ``"2024:3"``.  When supplied, only the
        vintages released in that round are returned; when ``None`` all
        vintages across rounds are included.

    Returns
    -------
    MonetaryPolicyDataResponse
        The model contains an ``external_id`` as echoed by the API and a
        list of :class:`ForecastVintage` objects (see attribute
        ``vintages``).

    """
    params: dict[str, Any] = {"series": series_id}
    if policy_round:
        params["policy_round_name"] = policy_round

    payload: dict[str, Any] = await riksbanken_request("", params)
    items: list[dict[str, Any]] = payload.get("data", []) or []
    if not items:
        return MonetaryPolicyDataResponse(external_id=series_id, vintages=[])

    raw = items[0]
    raw_vintages: list[dict[str, Any]] = raw.get("vintages", [])
    if isinstance(raw_vintages, dict):
        raw_vintages = [raw_vintages]

    for v in raw_vintages:
        # Determine cut‑off date for this vintage
        cutoff_str: str | None = v.get("metadata", {}).get(
            "forecast_cutoff_date"
        )  # type: ignore[index]
        cutoff_dt: date | None = None
        if cutoff_str:
            try:
                cutoff_dt = date.fromisoformat(cutoff_str)
            except ValueError:
                logger.warning(f"Malformed cutoff date '{cutoff_str}' in vintage.")

        # Annotate each observation
        for obs in v.get("observations", []):
            dt_str: str | None = obs.get("dt") or obs.get("date")
            is_fc = False
            if cutoff_dt and dt_str:
                try:
                    is_fc = date.fromisoformat(dt_str) > cutoff_dt
                except ValueError:
                    logger.debug(f"Bad observation date '{dt_str}' ignored.")

            # map into the new schema -------------------------------
            obs["forecast"] = obs["value"] if is_fc else None
            obs["observation"] = None if is_fc else obs["value"]
            obs["realized"] = None if is_fc else obs["value"]

        # -----------------------------------------------------------------
        # Pydantic‑validate each observation individually
        # -----------------------------------------------------------------
        v["observations"] = [
            ForecastObservation.model_validate(o)  # NEW
            for o in v.get("observations", [])
        ]

    # Validate after enrichment
    vintages_objs: list[ForecastVintage] = [
        ForecastVintage.model_validate(v) for v in raw_vintages
    ]

    return MonetaryPolicyDataResponse(
        external_id=raw.get("external_id", series_id),
        vintages=vintages_objs,
    )


async def _fetch_series(
    series_id: str,
    req: ForecastRequest,
    *,
    _fetcher: SeriesFetcher = get_policy_data,
) -> MonetaryPolicyDataResponse:
    base = await _fetcher(series_id, req.policy_round)

    if req.include_realized:
        rounds = await list_policy_rounds()
        if rounds.rounds:
            latest_round = max(rounds.rounds, key=lambda r: (r.year, r.iteration)).id
            if latest_round != req.policy_round:
                latest = await _fetcher(series_id, latest_round)
                if base.vintages and latest.vintages:
                    merged = merge_realized(base.vintages[0], latest.vintages[0])
                    base.vintages[0] = merged
    return base


# =============================================================================
# ──────────────────────────── Thematic wrappers ──────────────────────────────
# =============================================================================
# Each function corresponds to *one* Riksbank‑defined series.  Docstrings aim
# to teach economic interpretation and to show the exact series identifier.
# =============================================================================

# ─────────────────────────────── Real Economy ────────────────────────────────


async def get_gdp_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Gross Domestic Product, **calendar‑adjusted y/y growth**
    *(Series ID: `SEQGDPNAYCA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Use this series when you want growth rates that are **directly
    comparable across calendar quarters**—for instance in event–study
    regressions around GDP‑release days.
    • The calendar adjustment removes variation in the **number of working
    days**, leap years, Easter shifts, etc., but it **retains seasonal
    patterns**.
    • Because Statistics Sweden publishes these numbers first, they are the
    benchmark for **real‑time forecast evaluation**.
    """
    return await _fetch_series("SEQGDPNAYCA", req)


async def get_unemployment_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Unemployment rate, **seasonally adjusted LFS**
    Unit: **percent of labour force**.
    Note: Seasonally adjusted series.
    *(Series ID: `SEQLABUEASA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.
    """
    return await _fetch_series("SEQLABUEASA", req)


async def get_cpi_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Headline CPI, **y/y inflation (NSA)**
    Unit: Annual percentage change.
    *(Series ID: `SEMCPINAYNA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Reference rate for **wage and rent indexation clauses** in Sweden.
    """
    return await _fetch_series("SEMCPINAYNA", req)


async def get_cpif_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    CPIF, **y/y inflation – Riksbank’s operational target**
    Unit: Annual percentage change.
    The CPIF is the Riksbank’s target variable for inflation and
    is used as a basis for the Riksbank’s monetary policy decisions.
    In its monetary policy analysis, the Riksbank also studies price
    developments for various sub-groups of the CPIF.
    Unit: Annual percentage change.
    *(Series ID: `SEMCPIFNAYNA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.
    """
    return await _fetch_series("SEMCPIFNAYNA", req)


async def get_cpif_ex_energy_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    CPIF **excluding energy**, y/y – the Riksbank’s canonical *core* measure.
    Unit: Annual percentage change.
    A common approach is to exclude certain predetermined components from CPIF inflation,
    namely those that are considered to reflect more temporary and short-term movements
    in the measured inflation rate than the other components do.
    The CPIF excluding energy is an example of such a measure.
    *(Series ID: `SEMCPIFFEXYNA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.
    """
    return await _fetch_series("SEMCPIFFEXYNA", req)


async def get_hourly_labour_cost_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Hourly labour cost, **y/y change (National Accounts)**
    Unit: Annual percentage change.
    *(Series ID: `SEACOMNAYCA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Key ingredient in **unit‑labour‑cost (ULC)** calculations: combine with GDP per hour to diagnose competitiveness.
    """
    return await _fetch_series("SEACOMNAYCA", req)


async def get_hourly_wage_na_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Hourly wage, **National Accounts definition**, y/y
    Unit: Annual percentage change.
    Note: Calendar adjusted series.
    *(Series ID: `SEAWAGNAYCA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Evaluate **labour‑share dynamics**: pair with GDP at factor cost to see if wage income keeps up with productivity.
    """
    return await _fetch_series("SEAWAGNAYCA", req)


async def get_hourly_wage_nmo_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Hourly wage, **National Mediation Office (NMO) measure**, y/y
    Unit: Annual percentage change.
    *(Series ID: `SEAWAGKLYNA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Note that coverage is narrower (collectively‑agreed sectors), so match
    sample carefully in microdata studies.
    """

    return await _fetch_series("SEAWAGKLYNA", req)


async def get_population_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """Population level forecast (total population).

    Series ID: ``SEQPOPNAANA``.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Measured in *thousands of persons*.  Combine with GDP for per‑capita
    analyses.
    """
    return await _fetch_series("SEPOPYRCA", req)


async def get_employed_persons_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Number of **employed persons (LFS)**, seasonally adjusted
    Unit: Thousands of persons.
    *(Series ID: `SEQLABEPASA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.
    """

    return await _fetch_series("SEQLABEPASA", req)


async def get_labour_force_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Labour force, **seasonally adjusted level**
    Unit: Thousands of persons.
    *(Series ID: `SEQLABLFASA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Denominator for **participation‑rate** calculations: employment / labour force.
    Seasonal adjustment makes the series smoother than the raw LFS count.
    """
    return await _fetch_series("SEQLABLFASA", req)


async def get_gdp_gap_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Output gap (GDP gap), **percent of potential output**
    GDP gap refers to the deviation from the Riksbank's assessed long-term trend.
    Unit: Percent of potential output.
    *(Series ID: `SEQGDPGAPYSA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    **Note:** The Riksbank’s gap estimate embeds its own filter
    assumptions; results can differ from other estimates (e.g. OECD).
    """

    return await _fetch_series("SEQGDPGAPYSA", req)


async def get_policy_rate_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Policy (repo) rate, **quarterly mean**, percent.
    Unit: Percent.
    The policy rate is the rate that governs which rates the banks can
    deposit in and borrow money from the Riksbank. The banks' deposit and
    lending rates at the Riksbank in turn affect the banks' interest rates
    on loans and savings accounts.

    *(Series ID: `SEQRATENAYNA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.


    """
    return await _fetch_series("SEQRATENAYNA", req)


async def get_general_government_net_lending_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """General‑government net lending (% of GDP).
    Unit: Percent of GDP.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Series ID: ``SEAPBSNAYNA``.
    """
    return await _fetch_series("SEAPBSNAYNA", req)


# ──────────────── GDP level variants (calendar / seasonal adj.) ───────────────


async def get_gdp_level_saca_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Real GDP level, **seasonally *and* calendar‑adjusted** (SACA).

    **Unit**: million SEK, constant (chain‑linked) prices
    **Series ID**: `SEQGDPNAASA`

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    **What is adjusted?**
    • *Seasonal adjustment* removes predictable intra‑year production swings –
      e.g. Christmas shutdowns, summer vacations, harvest cycles – so each
      quarter reflects underlying momentum rather than the time of year.
    • *Calendar adjustment* removes distortions from the varying number of
      working days, moving holidays such as Easter, and leap‑year effects.

    Because **both** sources of systematic variation are stripped out, adjacent
    quarters are directly comparable; Q‑on‑Q growth rates capture genuine
    economic changes rather than calendar artefacts.
    """
    return await _fetch_series("SEQGDPNAASA", req)


async def get_gdp_level_ca_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Real GDP level, **calendar‑adjusted (seasonal pattern intact)** (CA).

    **Unit**: million SEK, constant (chain‑linked) prices
    **Series ID**: `SEQGDPNAACA`

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    **What is adjusted?**
    • *Calendar adjustment only* – effects from varying working‑day counts,
      leap years, and moveable feasts are removed so that each quarter has a
      comparable number of effective production days.

    **What remains?**
    • The *seasonal pattern* (regular intra‑year fluctuations) is **left
      untouched**. As a result, comparing the same quarter year‑over‑year (e.g.
      Q2 vs Q2) is meaningful, but quarter‑to‑quarter movements still follow
      the familiar seasonal rhythm.
    """
    return await _fetch_series("SEQGDPNAACA", req)


async def get_gdp_level_na_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Real GDP level, **non‑adjusted (NSA)**.

    **Unit**: million SEK, constant (chain‑linked) prices
    **Series ID**: `SEQGDPNAANA`

    **What is adjusted?**
    • Nothing – this is the raw series at constant prices. It still contains
      both seasonal swings *and* calendar effects.
    """
    return await _fetch_series("SEQGDPNAANA", req)


async def get_gdp_yoy_sa_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    GDP **y/y growth, seasonally *and* calendar‑adjusted**
    *(Series ID: `SEQGDPNAYSA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    **When to use**
    ----------------
    The full SA‑CA filter makes this series ideal for
    • **Cross‑country comparisons** where different holiday structures would
      otherwise distort the data,
    • Computing **annualised q/q growth chains**, and
    • Structural models that assume residuals are i.i.d. over the year.

    If you care about the precise wording used by Statistics Sweden on
    release day, use :func:`get_gdp_data` instead (calendar‑adjusted only).
    """
    return await _fetch_series("SEQGDPNAYSA", req)


async def get_gdp_yoy_na_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """GDP y/y growth, **non‑adjusted (NSA)**.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Series ID: ``SEQGDPNAYNA``.
    """
    return await _fetch_series("SEQGDPNAYNA", req)


# ─────────────────────────────── CPI level/changes ───────────────────────────


async def get_cpi_index_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """CPI index level (base 1980 = 100).

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Series ID: ``SEMCPINAANA``.
    """
    return await _fetch_series("SEMCPINAANA", req)


async def get_cpi_yoy_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """CPI y/y inflation (headline).

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Series ID: ``SEMCPINAYNA``.
    """
    return await _fetch_series("SEMCPINAYNA", req)


# ─────────────────────────────── CPIF variants ───────────────────────────────


async def get_cpif_yoy_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """CPIF y/y inflation—the **target variable**.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Series ID: ``SEMCPIFNAYNA``.
    """
    return await _fetch_series("SEMCPIFNAYNA", req)


async def get_cpif_ex_energy_index_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    CPIF **excluding energy, index level (1987 = 100)**
    *(Series ID: `SEMCPIFFEXANA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    **When to use**
    ----------------
    • Construct **core‑inflation fan charts**: convert the index to y/y
      growth to visualise uncertainty around underlying price trends.
    • Derive **real purchasing‑power series** by deflating nominal wages or
      household income with this index rather than headline CPI, thereby
      filtering out energy price noise.
    """
    return await _fetch_series("SEMCPIFFEXANA", req)


# ─────────────── Nominal exchange rate (KIX) – index level ───────────────────


async def get_nominal_exchange_rate_kix_index_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Nominal KIX exchange‑rate **index level**
    The exchange rate index weights together different bilateral exchange rates
    to create an effective (or average) exchange rate. By studying the exchange
    rate index, you can see how much the value of the krona has changed.
    A higher value in the index means that the krona has depreciated and a
    lower value means that the krona has appreciated.
    Unit: Index, 18 Nov 1992 = 100
    *(Series ID: `SEQKIXNAANA`, 18 Nov 1992 = 100)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    Remember: A **higher** KIX value means a **weaker** krona.
    """
    return await _fetch_series("SEQKIXNAANA", req)


# ────────────────────────────── Demographics ─────────────────────────────────


async def get_population_level_data(
    req: ForecastRequest,
) -> MonetaryPolicyDataResponse:
    """
    Population aged 15‑74, **level (thousands)**
    Unit: Thousands of persons.
    *(Series ID: `SEQPOPNAANA`)*.

    LLM call format
    ---------------
    Invoke the tool with one **JSON object** as argument, e.g.:

        {"policy_round": "2022:1", "include_realized": true}

    • Omit `"policy_round"` to retrieve every vintage.
    • Set `"include_realized": true` to append realised (out‑turn) values.

    """
    return await _fetch_series("SEQPOPNAANA", req)
