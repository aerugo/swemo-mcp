"""
MCP Server for Riksbank data (monetary policy, SWEA, SWESTR).
"""
import asyncio
from contextlib import asynccontextmanager
from mcp import FastMCP

from riksbanken_mcp.tools.monetary_policy_tools import (
    list_policy_rounds,
    list_series_ids,
    get_forecast_data,
    get_gdp_data,
    get_unemployment_data,
    get_cpi_data,
    get_cpif_data,
    get_cpif_ex_energy_data,
    get_hourly_labour_cost_data,
    get_hourly_wage_na_data,
    get_hourly_wage_nmo_data,
    get_nominal_exchange_rate_kix_data,
    get_population_data,
    get_employed_persons_data,
    get_labour_force_data
)
from riksbanken_mcp.tools.swea_tools import (
    get_policy_rate,
    get_usd_exchange_rate,
    get_eur_exchange_rate,
    get_gbp_exchange_rate,
    get_mortgage_rate
)
from riksbanken_mcp.tools.swestr_tools import (
    get_swestr,
    get_latest_swestr,
    get_swestr_averages,
    get_swestr_1week,
    get_swestr_1month
)

@asynccontextmanager
async def app_lifespan():
    # Setup code here (if needed)
    yield
    # Cleanup code here (if needed)

mcp = FastMCP(
    title="Riksbank MCP Server",
    description="Access to Riksbank monetary policy, SWEA, and SWESTR data",
    version="0.1.0",
    lifespan=app_lifespan
)

# Register Monetary Policy tools
mcp.tool(list_policy_rounds)
mcp.tool(list_series_ids)
mcp.tool(get_forecast_data)
mcp.tool(get_gdp_data)
mcp.tool(get_unemployment_data)
mcp.tool(get_cpi_data)
mcp.tool(get_cpif_data)
mcp.tool(get_cpif_ex_energy_data)
mcp.tool(get_hourly_labour_cost_data)
mcp.tool(get_hourly_wage_na_data)
mcp.tool(get_hourly_wage_nmo_data)
mcp.tool(get_nominal_exchange_rate_kix_data)
mcp.tool(get_population_data)
mcp.tool(get_employed_persons_data)
mcp.tool(get_labour_force_data)

# Register SWEA tools
mcp.tool(get_policy_rate)
mcp.tool(get_usd_exchange_rate)
mcp.tool(get_eur_exchange_rate)
mcp.tool(get_gbp_exchange_rate)
mcp.tool(get_mortgage_rate)

# Register SWESTR tools
mcp.tool(get_swestr)
mcp.tool(get_latest_swestr)
mcp.tool(get_swestr_averages)
mcp.tool(get_swestr_1week)
mcp.tool(get_swestr_1month)

def main() -> None:
    """
    Main entry point for the Riksbanken MCP server.
    """
    mcp.run("stdio")

if __name__ == "__main__":
    main()
