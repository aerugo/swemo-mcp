"""
MCP Server for Riksbank data (monetary policy, SWEA, SWESTR).
"""

import sys
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from mcp.server import FastMCP

from riksbank_mcp.tools.monetary_policy_tools import (
    get_cpi_data,
    get_cpi_index_data,
    get_cpi_yoy_data,
    get_cpif_data,
    get_cpif_ex_energy_data,
    get_cpif_ex_energy_index_data,
    get_cpif_yoy_data,
    get_employed_persons_data,
    get_gdp_data,
    get_gdp_gap_data,
    get_gdp_level_ca_data,
    get_gdp_level_na_data,
    get_gdp_level_saca_data,
    get_gdp_yoy_na_data,
    get_gdp_yoy_sa_data,
    get_general_government_net_lending_data,
    get_hourly_labour_cost_data,
    get_hourly_wage_na_data,
    get_hourly_wage_nmo_data,
    get_labour_force_data,
    get_nominal_exchange_rate_kix_index_data,
    get_policy_rate_data,
    get_population_data,
    get_population_level_data,
    get_unemployment_data,
    list_policy_rounds,
    list_series_ids,
)
from riksbank_mcp.tools.swea_tools import (
    get_calendar_days,
    get_cross_rate_aggregates,
    get_cross_rates,
    get_eur_exchange_rate,
    get_gbp_exchange_rate,
    get_group_details,
    get_latest_observation,
    get_mortgage_rate,
    get_observation_aggregates,
    get_policy_rate,
    get_series_info,
    get_usd_exchange_rate,
    list_exchange_rate_series,
    list_groups,
    list_series,
)
from riksbank_mcp.tools.swestr_tools import (
    get_latest_swestr,
    get_swestr,
    get_swestr_1month,
    get_swestr_1week,
    get_swestr_averages,
)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    print("[Riksbank MCP Lifespan] Starting lifespan setup...", file=sys.stderr)

    # (Optional) Pre-fetch or initialize Riksbank-specific resources here.
    context_data: dict[str, Any] = {}  # Populate with any needed data

    print(
        "[Riksbank MCP Lifespan] Initialization complete. All data cached.",
        file=sys.stderr,
    )
    print("[Riksbank MCP Lifespan] Yielding context...", file=sys.stderr)

    try:
        yield context_data
        print(
            "[Riksbank MCP Lifespan] Post-yield (server shutting down)...",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"[Riksbank MCP Lifespan] Exception DURING yield/server run?: {e}",
            file=sys.stderr,
        )
        traceback.print_exc(file=sys.stderr)
        raise
    finally:
        print(
            "[Riksbank MCP Lifespan] Entering finally block (shutdown).",
            file=sys.stderr,
        )
        print("[Riksbank MCP] Shutting down.", file=sys.stderr)


mcp = FastMCP(
    title="Riksbank MCP Server",
    description="Access to Riksbank monetary policy, SWEA, and SWESTR data",
    version="0.1.0",
    lifespan=app_lifespan,
)

# Register Monetary Policy tools
mcp.tool()(list_policy_rounds)
mcp.tool()(list_series_ids)
mcp.tool()(get_gdp_data)
mcp.tool()(get_unemployment_data)
mcp.tool()(get_cpi_data)
mcp.tool()(get_cpif_data)
mcp.tool()(get_cpif_ex_energy_data)
mcp.tool()(get_hourly_labour_cost_data)
mcp.tool()(get_hourly_wage_na_data)
mcp.tool()(get_hourly_wage_nmo_data)
mcp.tool()(get_population_data)
mcp.tool()(get_employed_persons_data)
mcp.tool()(get_labour_force_data)
mcp.tool()(get_gdp_level_saca_data)
mcp.tool()(get_gdp_level_ca_data)
mcp.tool()(get_gdp_level_na_data)
mcp.tool()(get_gdp_yoy_sa_data)
mcp.tool()(get_gdp_yoy_na_data)
mcp.tool()(get_cpi_index_data)
mcp.tool()(get_cpi_yoy_data)
mcp.tool()(get_cpif_yoy_data)
mcp.tool()(get_cpif_ex_energy_index_data)
mcp.tool()(get_nominal_exchange_rate_kix_index_data)
mcp.tool()(get_population_level_data)

# Register SWEA tools
mcp.tool()(get_policy_rate)
mcp.tool()(get_usd_exchange_rate)
mcp.tool()(get_eur_exchange_rate)
mcp.tool()(get_gbp_exchange_rate)
mcp.tool()(get_mortgage_rate)

# Register SWESTR tools
mcp.tool()(get_swestr)
mcp.tool()(get_latest_swestr)
mcp.tool()(get_swestr_averages)
mcp.tool()(get_swestr_1week)
mcp.tool()(get_swestr_1month)

# --- Additional SWEA Tools ---
mcp.tool()(get_observation_aggregates)
mcp.tool()(get_latest_observation)
mcp.tool()(get_calendar_days)
mcp.tool()(get_cross_rates)
mcp.tool()(get_cross_rate_aggregates)
mcp.tool()(list_groups)
mcp.tool()(get_group_details)
mcp.tool()(list_series)
mcp.tool()(get_series_info)
mcp.tool()(list_exchange_rate_series)

# --- Additional Monetary Policy Tools ---
mcp.tool()(get_gdp_gap_data)
mcp.tool()(get_policy_rate_data)
mcp.tool()(get_general_government_net_lending_data)


def main() -> None:
    """
    Main entry point for the Riksbanken MCP server.
    """
    import sys
    import traceback

    print("[Riksbank MCP] Starting server on stdio...", file=sys.stderr)
    try:
        mcp.run("stdio")
        print("[Riksbank MCP] Finished cleanly.", file=sys.stderr)
    except Exception as e:
        print(f"[Riksbank MCP] EXCEPTION: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    finally:
        print("[Riksbank MCP] Exiting.", file=sys.stderr)


if __name__ == "__main__":
    main()
