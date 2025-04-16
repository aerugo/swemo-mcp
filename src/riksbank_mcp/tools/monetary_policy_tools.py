"""
Riksbank Monetary‑Policy API helper functions
===========================================
"""

import logging
from typing import Any

from riksbank_mcp.models import (
    ForecastVintage,
    MonetaryPolicyDataResponse,
    MonetaryPolicyDataRoundsResponse,
    MonetaryPolicyDataSeriesResponse,
    PolicyRound,
    SeriesInfo,
)
from riksbank_mcp.services.monetary_policy_api import riksbanken_request

logger = logging.getLogger(__name__)


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
        raw_vintages = [raw_vintages]  # type: ignore[assignment]

    vintages_objs: list[ForecastVintage] = [
        ForecastVintage.model_validate(v) for v in raw_vintages  # Pydantic v2
    ]

    return MonetaryPolicyDataResponse(
        external_id=raw.get("external_id", series_id),
        vintages=vintages_objs,
    )


# =============================================================================
# ──────────────────────────── Thematic wrappers ──────────────────────────────
# =============================================================================
# Each function corresponds to *one* Riksbank‑defined series.  Docstrings aim
# to teach economic interpretation and to show the exact series identifier.
# =============================================================================

# ─────────────────────────────── Real Economy ────────────────────────────────


async def get_gdp_data(policy_round: str | None = None) -> MonetaryPolicyDataResponse:
    """
    Gross Domestic Product, **calendar‑adjusted y/y growth**
    *(Series ID: `SEQGDPNAYCA`)*.

    **When to use**
    ----------------
    Use this series when you want growth rates that are **directly
    comparable across calendar quarters**—for instance in event–study
    regressions around GDP‑release days.
    • The calendar adjustment removes variation in the **number of working
    days**, leap years, Easter shifts, etc., but it **retains seasonal
    patterns**.
    • Because Statistics Sweden publishes these numbers first, they are the
    benchmark for **real‑time forecast evaluation**.
    """
    return await get_policy_data("SEQGDPNAYCA", policy_round)


async def get_unemployment_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Unemployment rate, **seasonally adjusted LFS**
    Unit: **percent of labour force**.
    Note: Seasonally adjusted series.
    *(Series ID: `SEQLABUEASA`)*.
    """
    return await get_policy_data("SEQLABUEASA", policy_round)


async def get_cpi_data(policy_round: str | None = None) -> MonetaryPolicyDataResponse:
    """
    Headline CPI, **y/y inflation (NSA)**
    Unit: Annual percentage change.
    *(Series ID: `SEMCPINAYNA`)*.

    Reference rate for **wage and rent indexation clauses** in Sweden.
    """
    return await get_policy_data("SEMCPINAYNA", policy_round)


async def get_cpif_data(policy_round: str | None = None) -> MonetaryPolicyDataResponse:
    """
    CPIF, **y/y inflation – Riksbank’s operational target**
    Unit: Annual percentage change.
    The CPIF is the Riksbank’s target variable for inflation and
    is used as a basis for the Riksbank’s monetary policy decisions.
    In its monetary policy analysis, the Riksbank also studies price
    developments for various sub-groups of the CPIF.
    Unit: Annual percentage change.
    *(Series ID: `SEMCPIFNAYNA`)*.
    """
    return await get_policy_data("SEMCPIFNAYNA", policy_round)


async def get_cpif_ex_energy_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    CPIF **excluding energy**, y/y – the Riksbank’s canonical *core* measure.
    Unit: Annual percentage change.
    A common approach is to exclude certain predetermined components from CPIF inflation,
    namely those that are considered to reflect more temporary and short-term movements
    in the measured inflation rate than the other components do.
    The CPIF excluding energy is an example of such a measure.
    *(Series ID: `SEMCPIFFEXYNA`)*.
    """
    return await get_policy_data("SEMCPIFFEXYNA", policy_round)


async def get_hourly_labour_cost_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Hourly labour cost, **y/y change (National Accounts)**
    Unit: Annual percentage change.
    *(Series ID: `SEACOMNAYCA`)*.

    Key ingredient in **unit‑labour‑cost (ULC)** calculations: combine with GDP per hour to diagnose competitiveness.
    """
    return await get_policy_data("SEACOMNAYCA", policy_round)


async def get_hourly_wage_na_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Hourly wage, **National Accounts definition**, y/y
    Unit: Annual percentage change.
    Note: Calendar adjusted series.
    *(Series ID: `SEAWAGNAYCA`)*.

    Evaluate **labour‑share dynamics**: pair with GDP at factor cost to see if wage income keeps up with productivity.
    """
    return await get_policy_data("SEAWAGNAYCA", policy_round)


async def get_hourly_wage_nmo_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Hourly wage, **National Mediation Office (NMO) measure**, y/y
    Unit: Annual percentage change.
    *(Series ID: `SEAWAGKLYNA`)*.

    Note that coverage is narrower (collectively‑agreed sectors), so match
    sample carefully in microdata studies.
    """

    return await get_policy_data("SEAWAGKLYNA", policy_round)


async def get_population_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """Population level forecast (total population).

    Series ID: ``SEQPOPNAANA``.

    Measured in *thousands of persons*.  Combine with GDP for per‑capita
    analyses.
    """
    return await get_policy_data("SEPOPYRCA", policy_round)


async def get_employed_persons_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Number of **employed persons (LFS)**, seasonally adjusted
    Unit: Thousands of persons.
    *(Series ID: `SEQLABEPASA`)*.
    """

    return await get_policy_data("SEQLABEPASA", policy_round)


async def get_labour_force_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Labour force, **seasonally adjusted level**
    Unit: Thousands of persons.
    *(Series ID: `SEQLABLFASA`)*.

    Denominator for **participation‑rate** calculations: employment / labour force.
    Seasonal adjustment makes the series smoother than the raw LFS count.
    """
    return await get_policy_data("SEQLABLFASA", policy_round)


async def get_gdp_gap_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Output gap (GDP gap), **percent of potential output**
    GDP gap refers to the deviation from the Riksbank's assessed long-term trend.
    Unit: Percent of potential output.
    *(Series ID: `SEQGDPGAPYSA`)*.

    **Note:** The Riksbank’s gap estimate embeds its own filter
    assumptions; results can differ from other estimates (e.g. OECD).
    """

    return await get_policy_data("SEQGDPGAPYSA", policy_round)


async def get_policy_rate_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Policy (repo) rate, **quarterly mean**, percent.
    Unit: Percent.
    The policy rate is the rate that governs which rates the banks can
    deposit in and borrow money from the Riksbank. The banks' deposit and
    lending rates at the Riksbank in turn affect the banks' interest rates
    on loans and savings accounts.

    *(Series ID: `SEQRATENAYNA`)*.


    """
    return await get_policy_data("SEQRATENAYNA", policy_round)


async def get_general_government_net_lending_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """General‑government net lending (% of GDP).
    Unit: Percent of GDP.

    Series ID: ``SEAPBSNAYNA``.
    """
    return await get_policy_data("SEAPBSNAYNA", policy_round)


# ──────────────── GDP level variants (calendar / seasonal adj.) ───────────────


async def get_gdp_level_saca_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Real GDP level, **seasonally *and* calendar‑adjusted** (SACA).

    **Unit**: million SEK, constant (chain‑linked) prices
    **Series ID**: `SEQGDPNAASA`

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
    return await get_policy_data("SEQGDPNAASA", policy_round)


async def get_gdp_level_ca_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Real GDP level, **calendar‑adjusted (seasonal pattern intact)** (CA).

    **Unit**: million SEK, constant (chain‑linked) prices
    **Series ID**: `SEQGDPNAACA`

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
    return await get_policy_data("SEQGDPNAACA", policy_round)


async def get_gdp_level_na_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Real GDP level, **non‑adjusted (NSA)**.

    **Unit**: million SEK, constant (chain‑linked) prices
    **Series ID**: `SEQGDPNAANA`

    **What is adjusted?**
    • Nothing – this is the raw series at constant prices. It still contains
      both seasonal swings *and* calendar effects.
    """
    return await get_policy_data("SEQGDPNAANA", policy_round)


async def get_gdp_yoy_sa_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    GDP **y/y growth, seasonally *and* calendar‑adjusted**
    *(Series ID: `SEQGDPNAYSA`)*.

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
    return await get_policy_data("SEQGDPNAYSA", policy_round)


async def get_gdp_yoy_na_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """GDP y/y growth, **non‑adjusted (NSA)**.

    Series ID: ``SEQGDPNAYNA``.
    """
    return await get_policy_data("SEQGDPNAYNA", policy_round)


# ─────────────────────────────── CPI level/changes ───────────────────────────


async def get_cpi_index_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """CPI index level (base 1980 = 100).

    Series ID: ``SEMCPINAANA``.
    """
    return await get_policy_data("SEMCPINAANA", policy_round)


async def get_cpi_yoy_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """CPI y/y inflation (headline).

    Series ID: ``SEMCPINAYNA``.
    """
    return await get_policy_data("SEMCPINAYNA", policy_round)


# ─────────────────────────────── CPIF variants ───────────────────────────────


async def get_cpif_yoy_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """CPIF y/y inflation—the **target variable**.

    Series ID: ``SEMCPIFNAYNA``.
    """
    return await get_policy_data("SEMCPIFNAYNA", policy_round)


async def get_cpif_ex_energy_index_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    CPIF **excluding energy, index level (1987 = 100)**
    *(Series ID: `SEMCPIFFEXANA`)*.

    **When to use**
    ----------------
    • Construct **core‑inflation fan charts**: convert the index to y/y
      growth to visualise uncertainty around underlying price trends.
    • Derive **real purchasing‑power series** by deflating nominal wages or
      household income with this index rather than headline CPI, thereby
      filtering out energy price noise.
    """
    return await get_policy_data("SEMCPIFFEXANA", policy_round)


# ─────────────── Nominal exchange rate (KIX) – index level ───────────────────


async def get_nominal_exchange_rate_kix_index_data(
    policy_round: str | None = None,
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

    Remember: A **higher** KIX value means a **weaker** krona.
    """
    return await get_policy_data("SEQKIXNAANA", policy_round)


# ────────────────────────────── Demographics ─────────────────────────────────


async def get_population_level_data(
    policy_round: str | None = None,
) -> MonetaryPolicyDataResponse:
    """
    Population aged 15‑74, **level (thousands)**
    Unit: Thousands of persons.
    *(Series ID: `SEQPOPNAANA`)*.

    """
    return await get_policy_data("SEQPOPNAANA", policy_round)
