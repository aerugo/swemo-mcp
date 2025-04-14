# Riksbanken MCP Server

An MCP Server for accessing macroeconomic and financial data from the Riksbank. This server provides tools for retrieving data about monetary policy forecasts, exchange and interest rate data (via SWEA), and short-term money market rates (via SWESTR). It is built using asynchronous programming with `httpx` and uses `pydantic` for data validation.

## Features

- **Monetary Policy Tools**
  - List all monetary policy rounds.
  - Retrieve forecast data for key economic indicators (GDP, unemployment, CPI, CPIF, CPIF ex-energy, hourly labour cost, wages (NA and NMO), population, employment, labour force).

- **SWEA Tools**
  - Fetch the official policy (repo) rate.
  - Retrieve exchange rate series (USD/SEK, EUR/SEK, GBP/SEK).
  - Retrieve average mortgage interest rates.

- **SWESTR Tools**
  - Retrieve daily SWESTR (Swedish Short Term Rate) and its latest published value.
  - Retrieve compounded averages (e.g., 1-week, 1-month).

- **Modern, Asynchronous, and Type-Safe**
  - Fully asynchronous, using Python 3.13's async/await and `httpx` for network requests.
  - Uses `pydantic` models for robust data validation and self-documenting API responses.

## Installation

Ensure you have Python 3.13 or higher installed. Then, install the package in editable mode:

```bash
pip install -e .
```

This will install the required dependencies as specified in `pyproject.toml` (including `mcp`, `httpx`, and `pydantic`).

## Running the Server

### Using the CLI

After installation, you can launch the MCP server with the CLI command:

```bash
riksbanken-mcp
```

### Via Python Module

Alternatively, run the server directly using:

```bash
python -m riksbank_mcp.server
```

The server uses the stdio transport to communicate and registers all MCP tools.

## Repository Structure

```
riksbank_mcp/
├── __init__.py             # Package version and initialization
├── server.py               # Main MCP server entry point and tool registration
├── models.py               # Pydantic models for API responses and data validation
├── services/
│   ├── __init__.py         # Services package initialization
│   ├── monetary_policy_api.py  # Helper for the Monetary Policy API
│   ├── swea_api.py         # Helper for the SWEA API
│   └── swestr_api.py       # Helper for the SWESTR API
├── tools/
│   ├── __init__.py         # Tools package initialization
│   ├── monetary_policy_tools.py  # Tools for Monetary Policy data
│   ├── swea_tools.py       # Tools for SWEA data (policy rate, exchange rates, mortgage rate)
│   └── swestr_tools.py     # Tools for SWESTR data (short term rates and averages)
└── pyproject.toml          # Build and dependency configuration
```

## Usage Examples

### Example: Fetching GDP Forecast Data

```python
import asyncio
from riksbank_mcp.tools.monetary_policy_tools import get_gdp_data

async def main():
    # Retrieve forecast data for GDP for a specific policy round.
    gdp_forecast = await get_gdp_data("2023:4")
    for obs in gdp_forecast.observations:
        print(f"Date: {obs.date}, GDP forecast: {obs.value} (billion SEK)")

asyncio.run(main())
```

### Example: Retrieving the Latest SWESTR Rate

```python
import asyncio
from riksbank_mcp.tools.swestr_tools import get_latest_swestr

async def main():
    latest = await get_latest_swestr()
    print(f"Latest SWESTR: {latest.date} - {latest.value}%")

asyncio.run(main())
```

### Example: Retrieving USD/SEK Exchange Rates

```python
import asyncio
from riksbank_mcp.tools.swea_tools import get_usd_exchange_rate

async def main():
    usd_data = await get_usd_exchange_rate()
    for obs in usd_data.observations[-5:]:
        print(f"{obs.date}: {obs.value} SEK per USD")

asyncio.run(main())
```

## Testing

We use `pytest` along with `pytest-asyncio` for testing. Run the test suite using:

```bash
pytest
```

## Contributing

Contributions are welcome! When submitting changes, please adhere to the following principles:
- Follow PEP 8 and Python 3.13's type hinting conventions.
- Use asynchronous programming consistently.
- Update docstrings and Pydantic models accordingly.
- Ensure new tools or changes are covered with tests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Additional Resources

- [Riksbank API Documentation](https://www.riksbank.se)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [httpx Documentation](https://www.python-httpx.org/)
