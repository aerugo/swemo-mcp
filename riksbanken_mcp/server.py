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
    get_gdp_data
)
from riksbanken_mcp.tools.swea_tools import (
    get_policy_rate,
    get_usd_exchange_rate
)
from riksbanken_mcp.tools.swestr_tools import (
    get_swestr,
    get_latest_swestr
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

# Register SWEA tools
mcp.tool(get_policy_rate)
mcp.tool(get_usd_exchange_rate)

# Register SWESTR tools
mcp.tool(get_swestr)
mcp.tool(get_latest_swestr)

if __name__ == "__main__":
    mcp.run("stdio")
