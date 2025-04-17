# A Swedish Monetary‑Policy Data MCP Server

[![License: Apache‑2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![https://modelcontextprotocol.io](https://badge.mcpx.dev?type=server 'MCP Server')](https://modelcontextprotocol.io)

SwemoMCO is an unofficial **Monetary‑Policy Data MCP Server** wraps Sveriges Riksbank’s open API in a [Model‑Context‑Protocol](https://modelcontextprotocol.io/) (MCP) micro‑service.  It turns the raw REST end‑points into **typed Python tools** that can be invoked by LLMs or by humans through any MCP Client.

This edition of the README assumes you are using **[Astral’s `uv`](https://github.com/astral-sh/uv)** for dependency management and execution.

---

## Table of Contents

1. [Why this exists](#why-this-exists)
2. [The underlying data](#the-underlying-data)
   * [Policy rounds](#policy-rounds)
   * [Series identifiers](#series-identifiers)
   * [Forecast vintages & observations](#forecast-vintages--observations)
3. [How the MCP server works](#how-the-mcp-server-works)
   * [Architecture](#architecture)
   * [Catalogue of tools](#catalogue-of-tools)
4. [Installation](#installation)
5. [Quick‑start](#quick-start)
6. [Examples (Analysts & Journalists)](#examples-analysts--journalists)
7. [Docker](#docker)
8. [Development](#development)
9. [License](#license)

---

## Why this exists

Working with monetary‑policy data can be complicated: the raw API
requires hand‑crafted queries and knowledge of the different series.
This project:

* hides the HTTP plumbing behind a **clean, async Python interface**,
* exposes every series as an **MCP tool** discoverable by LLMs – allowing
  Claude Desktop and other MCP client tools to fetch Swedish
  macro data on demand.

As of 2020, the Riksbank’s service now includes both forecast values and
**realised (observed) data** once official figures are published. This
makes the dataset suitable for **historical analysis** (e.g. “What
actually happened to inflation in 2022?”) and for **forecast queries**
(e.g. “What does the Riksbank project for GDP next year?”).

---

## The underlying data

### Policy rounds

The Riksbank publishes a fresh set of forecasts four to five times a year.
Each publication is labelled `YYYY:I` (e.g. `2025:2` for the second release in 2025).

### Series identifiers

Every time‑series name follows the pattern

```
COUNTRY‑FREQUENCY‑AREA‑DECOMPOSITION‑UNIT‑ADJUSTED
```

Example: `SEQGDPNAYCA`  →  Sweden (`SE`), Quarterly (`Q`), GDP (`GDP`),
National‑Accounts decomposition (`NA`), *y/y* change (`Y`), Calendar
adjusted (`CA`).  Discover the catalogue with

```http
GET /forecasts/series_ids
```

### Forecast vintages & observations

Each **policy round** gives rise to a new “vintage” of forecasts for key
macroeconomic variables. Meanwhile, as data on actual outcomes get published,
the Riksbank updates its **realised observations**. This means you can:

- **Pin** a specific policy round (e.g. `"2024:1"`) to see only the forecasts
  from that round along with any observations available up through that round.
- Use `"latest"` to retrieve **all historical observations** (the final realised
  values known today) **plus** the newest forecast vintage. This is ideal for
  historical analysis—especially if you want to see the final, revised or
  actual values rather than the older forecasts.

Forecast metadata example:

```jsonc
{
  "revision_dtm": "2024‑07‑02T08:55:00Z",
  "forecast_cutoff_date": "2024‑06‑18",
  "policy_round": "2024:3",
  "policy_round_end_dtm": "2024‑07‑02T09:30:00Z"
}
```

---

## How the MCP server works

### Architecture

```text
┌─────────────────────────────────────────────────────────┐
│  FastMCP Server (src/swemo_mcp/server.py)           │
│                                                         │
│  • registers ≈30 *tools* (one per economic series)       │
│  • exposes them on stdio / SSE / HTTP                   │
└───────────────▲──────────────────────────────▲──────────┘
                │                              │
         async httpx                     LLM / user
                │                              │
┌───────────────┴────────────┐        ┌────────┴──────────┐
│ Riksbank REST API          │        │ mcp‑cli / ChatGPT │
└────────────────────────────┘        └───────────────────┘
```

* **`services/monetary_policy_api.py`** – thin async wrapper with
  automatic **exponential back‑off** (max‑retry on HTTP 429).
* **`tools/monetary_policy_tools.py`** – one declarative function per
  series; docstrings double as LLM prompts.
* **Pydantic v2 models** in `models.py` ensure every response has the
  expected schema.

### Catalogue of tools

| Tool | Series ID | Description |
|------|-----------|-------------|
| `get_gdp_data` | `SEQGDPNAYCA` | GDP y/y, calendar‑adjusted |
| `get_unemployment_data` | `SEQLABUEASA` | LFS unemployment rate |
| `get_cpi_data` | `SEMCPINAYNA` | Headline CPI y/y |
| … | … | _≈ 30 series in total – run `list_series_ids()` for the full list._ |

Each tool signature is:

```python
async def get_<series>_data(policy_round: str | None = None) -> MonetaryPolicyDataResponse
```

Pass `policy_round="2024:3"` to pin the vintage; omit for the complete
history.  For final historical data, pass `policy_round="latest"` so that
the tool merges all realised (observed) data points.

---

## Installation

> **Prerequisites:**
> * Python ≥ 3.12 (uses `typing.TypeAlias`/PEP 604 unions)
> * [Astral `uv`](https://github.com/astral-sh/uv) ≥ 0.2.0

Clone and set up the project with one command:

```bash
uv sync
```

`uv sync` installs all production and development dependencies declared in
`pyproject.toml`, creates a virtual environment if needed, and locks the
exact versions so every contributor or CI pipeline uses the same stack.

---

## Claude Desktop Integration

Edit your `claude_desktop_config.json` to add Kolada MCP Server:

### Docker Image (Local Build)
```json
"SwemoMCP": {
  "args": [
    "run",
    "-i",
    "--rm",
    "--name",
    "swemo-mcp-managed",
    "swemo-mcp:local"
  ],
  "command": "docker",
  "env": {}
}
```

### Prebuilt Container via PyPI
```json
"SwemoPyPI": {
  "args": ["swemo-mcp"],
  "command": "/Users/hugi/.cargo/bin/uvx"
}
```

### Local UV Execution (without Docker)
Replace `[path to kolada-mcp]` with your local directory:
```json
"SwemoLocal": {
  "args": [
    "--directory",
    "[path to kolada-mcp]/src/kolada_mcp",
    "run",
    "kolada-mcp"
  ],
  "command": "uv"
}
```

Restart Claude Desktop after updating.

## Use as a library

```python
import asyncio
from swemo_mcp.tools import get_policy_rate_data

async def main():
    from swemo_mcp.query import ForecastRequest
    req = ForecastRequest(policy_round="2023:4", include_realised=True)
    data = await get_policy_rate_data(req)
    print(data.vintages[0].observations[:5])  # first 5 observations

asyncio.run(main())
```

Because everything is typed and async, you can integrate the tools directly
into notebooks, dashboards, or other services.

---

## Docker

The project ships with a multi‑stage Dockerfile that uses `uv` in the final
layer, so container builds benefit from deterministic dependency resolution.

```bash
docker build -t swemo-mcp:latest .

docker run -i --rm swemo-mcp:latest | mcp chat
```

If you prefer **Docker Compose** for development, a sample `compose.yaml`
illustrates how to mount the source directory and hot‑reload changes.

---

## Development

1. **Set up the environment**:

   ```bash
   uv sync --dev
   ```

2. **Run the server in dev‑mode with live‑reload** (requires [`mcp dev`](https://github.com/modelcontextprotocol/dev)):

   ```bash
   uv run mcp dev src/swemo_mcp/server.py
   ```

3. **Open the MCP Inspector** to test and debug:

   <http://localhost:5173>

4. **Run the test‑suite** (pytest + asyncio):

   ```bash
   uv run pytest -q
   ```

5. **Format & lint** automatically with Ruff:

   ```bash
   uv run ruff check . --fix
   ```

---

## License

Licensed under the **Apache 2.0** license. See [`LICENSE`](LICENSE) for the
full text.

---

## Disclaimers

- This is an **unofficial** MCP server for the Riksbank’s data. The
  underlying API is subject to change, and this project may not always
  reflect the latest updates.
- Sveriges Riksbank has had no involvement in the development of this
  project. The data is provided "as is" without any warranty of any kind.
- The Riksbank’s data is subject to its own terms of use. Please refer to
  the [Riksbank’s API portal](https://developer.api.riksbank.se/) for
  more information.

