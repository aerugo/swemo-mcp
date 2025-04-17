# Riksbanken MCP Server
# Riksbank Monetary‑Policy Data MCP Server

[![PyPI version](https://img.shields.io/pypi/v/riksbank-mcp.svg)](https://pypi.org/project/riksbank-mcp)
[![Build](https://github.com/aerugo/riksbank-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/aerugo/riksbank-mcp/actions)
[![License: Apache‑2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Access Swedish monetary‑policy forecasts & outcomes _as code_.**

The unofficial **Monetary‑Policy Data MCP Server** wraps Sveriges Riksbank’s open API for
forecasts and realised outcomes (2020‑present) in a [Model‑Context‑Protocol](https://modelcontextprotocol.io/) (MCP) micro‑service.  It turns the raw REST end‑points into **typed Python tools** that can be invoked by LLMs or by humans through the [MCP CLI](https://github.com/modelcontext/mcp-cli).

---

## Table of Contents

1. [Why this exists](#why-this-exists)
2. [The underlying data](#the-underlying-data)
   * [Policy rounds](#policy-rounds)
   * [Series identifiers](#series-identifiers)
   * [Forecast vintages](#forecast-vintages)
3. [How the MCP server works](#how-the-mcp-server-works)
   * [Architecture](#architecture)
   * [Catalogue of tools](#catalogue-of-tools)
4. [Installation](#installation)
5. [Quick‑start](#quick-start)
6. [Docker](#docker)
7. [Development](#development)
8. [License](#license)

---

## Why this exists

Working with **real‑time monetary‑policy data** is painful: the raw API
requires hand‑crafted queries, and each response must be normalised
before analysis.  This project

* hides the HTTP plumbing behind a **clean, async Python interface**,
* provides **data‑class validation** (via *pydantic v2*) so that upstream
  code sees _guaranteed_ field names and types, and
* exposes every series as an **MCP tool** discoverable by LLMs – allowing
  Claude Desktop and other MCP client tools to fetch Swedish
  macro data on demand.

---

## The underlying data

### Policy rounds

The Riksbank publishes a fresh set of forecasts four times a year – in
three **Monetary‑Policy Reports (MPR)** and one shorter **Monetary‑Policy
Update (MPU)**.  Each publication is labelled `YYYY:I` (e.g. `2025:2` for
the second release in 2025).  

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

### Forecast vintages

Forecasts are delivered **vintage‑style**.  A single series can have
multiple `vintages`, each tagged with metadata:

```jsonc
{
  "revision_dtm": "2024‑07‑02T08:55:00Z",
  "forecast_cutoff_date": "2024‑06‑18",
  "policy_round": "2024:3",
  "policy_round_end_dtm": "2024‑07‑02T09:30:00Z"
}
```

`observations` then contain the time‑stamped numbers.

> **Transparency note:** The compilation includes both forecasts and
> realised outcomes (once Statistics Sweden has published them).

---

## How the MCP server works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  FastMCP Server (src/riksbank_mcp/server.py)           │
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
| `get_gdp_forecast_data` | `SEQGDPNAYCA` | GDP y/y, calendar‑adjusted |
| `get_unemployment_forecast_data` | `SEQLABUEASA` | LFS unemployment rate |
| `get_cpi_forecast_data` | `SEMCPINAYNA` | Headline CPI y/y |
| … | … | _≈ 30 series in total – run `list_forecast_series_ids()` for the full list._ |

Each tool signature is:

```python
async def get_<series>_forecast_data(policy_round: str | None = None) -> MonetaryPolicyDataResponse
```

Pass `policy_round="2024:3"` to pin the vintage; omit for the complete
history.

---

## Installation

### Prerequisites

* Python ≥ 3.12 (uses `typing.TypeAlias`/`|` unions)
* Optional: [poetry](https://python-poetry.org/) or `pipx`

```bash
pip install riksbank-mcp
```

### From source

```bash
git clone https://github.com/aerugo/riksbank-mcp.git
cd riksbank-mcp
pip install .[dev]
```

---

## Quick start

### 1. Run the server (stdio)

```bash
riksbank-mcp | mcp chat
```

### 2. Ask the LLM

```
> What was the Riksbank’s CPIF forecast in policy‑round 2024:1?
```

Under the hood the model calls

```python
await get_cpif_forecast_data("2024:1")
```

and returns a structured JSON payload.

### 3. Use as a library

```python
import asyncio
from riksbank_mcp.tools import get_policy_rate_forecast_data

async def main():
    from riksbank_mcp.query import ForecastRequest
    req = ForecastRequest(policy_round="2023:4", include_realized=True)
    data = await get_gdp_forecast_data(req)
    latest = data.vintages[-1].observations[-1]
    print(latest.dt, latest.value)

asyncio.run(main())
```

## License

Licensed under the **Apache 2.0** license.  See [LICENSE](LICENSE) for
full text.
