"""
MCP Server for Riksbank data (monetary policy, SWEA, SWESTR).
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict
import sys
import traceback

from mcp.server import FastMCP
from riksbank_mcp.tools.monetary_policy_tools import (
    get_cpi_data,
    get_cpif_data,
    get_cpif_ex_energy_data,
    get_employed_persons_data,
    get_forecast_data,
    get_gdp_data,
    get_hourly_labour_cost_data,
    get_hourly_wage_na_data,
    get_hourly_wage_nmo_data,
    get_labour_force_data,
    get_nominal_exchange_rate_kix_data,
    get_population_data,
    get_unemployment_data,
    list_policy_rounds,
    list_series_ids,
)
from riksbank_mcp.tools.swea_tools import (
    get_eur_exchange_rate,
    get_gbp_exchange_rate,
    get_mortgage_rate,
    get_policy_rate,
    get_usd_exchange_rate,
)
from riksbank_mcp.tools.swestr_tools import (
    get_latest_swestr,
    get_swestr,
    get_swestr_1month,
    get_swestr_1week,
    get_swestr_averages,
)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    print("[Riksbank MCP Lifespan] Starting lifespan setup...", file=sys.stderr)

    # (Optional) Pre-fetch or initialize Riksbank-specific resources here.
    context_data: Dict[str, Any] = {}  # Populate with any needed data

    print("[Riksbank MCP Lifespan] Initialization complete. All data cached.", file=sys.stderr)
    print("[Riksbank MCP Lifespan] Yielding context...", file=sys.stderr)

    try:
        yield context_data
        print("[Riksbank MCP Lifespan] Post-yield (server shutting down)...", file=sys.stderr)
    except Exception as e:
        print(f"[Riksbank MCP Lifespan] Exception DURING yield/server run?: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise
    finally:
        print("[Riksbank MCP Lifespan] Entering finally block (shutdown).", file=sys.stderr)
        print("[Riksbank MCP] Shutting down.", file=sys.stderr)


mcp = FastMCP(
    title="Riksbank MCP Server",
    description="Access to Riksbank monetary policy, SWEA, and SWESTR data",
    version="0.1.0",
    lifespan=app_lifespan,
)

# Register Monetary Policy tools
mcp.tool()(list_policy_rounds)  # type: ignore[Context]
mcp.tool()(list_series_ids)  # type: ignore[Context]
mcp.tool()(get_forecast_data)  # type: ignore[Context]
mcp.tool()(get_gdp_data)  # type: ignore[Context]
mcp.tool()(get_unemployment_data)  # type: ignore[Context]
mcp.tool()(get_cpi_data)  # type: ignore[Context]
mcp.tool()(get_cpif_data)  # type: ignore[Context]
mcp.tool()(get_cpif_ex_energy_data)  # type: ignore[Context]
mcp.tool()(get_hourly_labour_cost_data)  # type: ignore[Context]
mcp.tool()(get_hourly_wage_na_data)  # type: ignore[Context]
mcp.tool()(get_hourly_wage_nmo_data)  # type: ignore[Context]
mcp.tool()(get_nominal_exchange_rate_kix_data)  # type: ignore[Context]
mcp.tool()(get_population_data)  # type: ignore[Context]
mcp.tool()(get_employed_persons_data)  # type: ignore[Context]
mcp.tool()(get_labour_force_data)  # type: ignore[Context]

# Register SWEA tools
mcp.tool()(get_policy_rate)  # type: ignore[Context]
mcp.tool()(get_usd_exchange_rate)  # type: ignore[Context]
mcp.tool()(get_eur_exchange_rate)  # type: ignore[Context]
mcp.tool()(get_gbp_exchange_rate)  # type: ignore[Context]
mcp.tool()(get_mortgage_rate)  # type: ignore[Context]

# Register SWESTR tools
mcp.tool()(get_swestr)  # type: ignore[Context]
mcp.tool()(get_latest_swestr)  # type: ignore[Context]
mcp.tool()(get_swestr_averages)  # type: ignore[Context]
mcp.tool()(get_swestr_1week)  # type: ignore[Context]
mcp.tool()(get_swestr_1month)  # type: ignore[Context]


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
