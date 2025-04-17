# MCP Python Server Conventions

This document provides style and design conventions for writing Python MCP servers.

----

## Table of Contents

1. [Environment](#environment)  
2. [General Principles](#general-principles)  
3. [Design Principles for MCP Servers](#design-principles-for-mcp-servers)  
4. [Coding Standards](#coding-standards)  
   - [Type Hints](#type-hints)  
   - [Docstrings](#docstrings)  
   - [Naming Conventions](#naming-conventions)  
5. [MCP Server Structure](#mcp-server-structure)  
   - [Server Initialization](#server-initialization)  
   - [Tools](#tools)  
   - [Resources](#resources)  
   - [Prompts](#prompts)  
   - [Lifespan and Context](#lifespan-and-context)  
6. [Async Concurrency](#async-concurrency)  
7. [Testing and Quality](#testing-and-quality)  
8. [Logging and Observability](#logging-and-observability)  
9. [Security and Validation](#security-and-validation)  
10. [Additional Tips](#additional-tips)  

----

## 1. Environment

- **Python Version**: Target Python **3.13**.  
- **Recommended Libraries**:  
  - [`mcp` Python SDK](https://modelcontextprotocol.io/)  
  - [`pydantic`](https://docs.pydantic.dev/) (Version **2.x**) for optional data validation.

----

## 2. General Principles

1. **Keep it Simple**: MCP servers are meant to be easily discoverable by LLMs and straightforward to use. Avoid overly complex abstractions.  
2. **Follow PEP 8**: Use standard Python style (PEP 8) for readability and consistency.  
3. **Leverage Async**: MCP I/O is inherently asynchronous. Embrace `async/await` for I/O-bound operations.  
4. **Use Clear Interfaces**: Where possible, define behaviors with `Protocol` or minimal class interfaces.  
5. **Document Thoroughly**: Write clear docstrings for tools, resources, and prompts. This is crucial because LLMs rely on docstrings to understand usage.  

----

## 3. Design Principles for MCP Servers

### 3.1 Favor Composition Over Inheritance

- **MCP Entities** (Tools, Resources, Prompts) should be added to your server instance using decorators, rather than implementing large inheritance hierarchies.
- Use small, composable functions or classes (for example, small utility classes for database connections, or a simple function for an HTTP request).

### 3.2 High Cohesion, Low Coupling

- Each tool, resource, or prompt should handle a single responsibility.
- Keep your server’s structure modular: break down complex interactions into smaller, well-defined functionalities.

### 3.3 Start with the Data (When Needed)

- In many MCP servers, data modeling can be minimal. However, if your server manages structured data, define **Pydantic** models (or plain dataclasses) first. 
- For argument validation, consider using **Pydantic** models or field validators to ensure your tool is called with correct data.

### 3.4 Depend on Abstractions

- For external interactions (e.g., databases, APIs), rely on simple interfaces or Protocols. This makes it easier to swap implementations, test, or modify logic without breaking your server design.

### 3.5 Separate Creation from Use

- Use server lifespan for initialization (e.g., open connections, load config). Inject these as needed in your tools/resources so logic remains testable and decoupled.

----

## 4. Coding Standards

### 4.1 Type Hints

1. **Use built-in generics** in Python 3.13: `list[str]`, `dict[str, float]`, `tuple[int, str]`.  
2. **Import from `typing`** for Protocols, Callable, TypeVar, etc.  
3. **Use `|` for union types**: `str | None`.  
4. **Annotate all function parameters and return types** (including async functions).  
5. **Forward references** are typically not needed with Python 3.13 but use them if your code structure requires referencing models before they’re fully defined.  

<details>
<summary>Example</summary>

```python
async def process_data(data: list[int | str]) -> dict[str, int]:
    ...
```
</details>

### 4.2 Docstrings

- Use [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) or [reStructuredText](https://www.python.org/dev/peps/pep-0287/) format.  
- Clearly describe the purpose, parameters, and return values.  
- For **Tools** and **Resources**, docstrings double as usage instructions for LLMs, so describe them carefully.

<details>
<summary>Example</summary>

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers.

    Args:
        a: The first integer.
        b: The second integer.

    Returns:
        The sum of the two numbers.
    """
    return a + b
```
</details>

### 4.3 Naming Conventions

- **Modules**: `snake_case` (e.g., `user_tools.py`, `db_utils.py`).  
- **Classes**: `PascalCase` (e.g., `DatabaseClient`).  
- **Functions**: `snake_case` (e.g., `fetch_data`).  
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`).  
- **MCP Entities**:  
  - Tools: `snake_case` function name with an `@mcp.tool()` decorator.  
  - Resources: `snake_case` function name with an `@mcp.resource("...")` decorator.  
  - Prompts: `snake_case` function name with an `@mcp.prompt()` decorator.  

----

## 5. MCP Server Structure

Below is a recommended structure to keep your MCP server organized:

```
my_mcp_server/
├── __init__.py
├── server.py
├── tools/
│   ├── __init__.py
│   ├── data_tools.py
│   └── compute_tools.py
├── resources/
│   ├── __init__.py
│   └── config_resources.py
├── prompts/
│   ├── __init__.py
│   └── code_review_prompts.py
└── tests/
    └── test_server.py
```

### 5.1 Server Initialization

Create a single entry point (e.g., `server.py`) that initializes the server:

```python
from mcp.server.fastmcp import FastMCP
from .tools.data_tools import fetch_data
from .resources.config_resources import get_config
from .prompts.code_review_prompts import review_code

mcp = FastMCP("My MCP Server")

# Register Tools
mcp.tool()(fetch_data)

# Register Resources
mcp.resource("config://app")(get_config)

# Register Prompts
mcp.prompt()(review_code)

if __name__ == "__main__":
    mcp.run()
```

### 5.2 Tools

- **Stateless** or minimal side effects whenever possible.  
- Provide docstrings that clearly explain parameters.  
- Return simple Python objects or strings; if returning binary data, consider using `mcp.server.fastmcp.Image`.  

<details>
<summary>Example</summary>

```python
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculate BMI given weight in kg and height in meters.
    """
    return weight_kg / (height_m ** 2)
```
</details>

### 5.3 Resources

- Represent data that is read frequently but rarely changed.  
- Avoid heavy computation or side effects.  
- Use the resource URI pattern to capture dynamic parameters.

<details>
<summary>Example</summary>

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: str) -> dict[str, str]:
    """
    Fetch user profile data for a given user_id.
    """
    # Example logic
    return {
        "name": "John Doe",
        "id": user_id,
        "role": "admin",
    }
```
</details>

### 5.4 Prompts

- Define conversation scaffolds or user interaction templates.  
- Return plain strings or lists of message objects as needed.  

<details>
<summary>Example</summary>

```python
from mcp.server.fastmcp.prompts import base

@mcp.prompt()
def review_code(code: str) -> str:
    """
    Prompt for reviewing code.
    """
    return f"Please review this code:\n\n{code}"

@mcp.prompt()
def debug_error(error_message: str) -> list[base.Message]:
    """
    Prompt for debugging an error message.
    """
    return [
        base.UserMessage("I encountered an error:"),
        base.UserMessage(error_message),
        base.AssistantMessage("Could you provide more context?"),
    ]
```
</details>

### 5.5 Lifespan and Context

- Use the server’s `lifespan` to manage resources (e.g., DB connections, cached objects).  
- Access them through the `ctx.request_context.lifespan_context` (or `ctx` argument) within tools or resources.

<details>
<summary>Example</summary>

```python
from contextlib import asynccontextmanager
from typing import AsyncIterator
from mcp.server.fastmcp import FastMCP, Context

class Database:
    async def connect(self):
        print("Database connected.")

    async def disconnect(self):
        print("Database disconnected.")

    def query(self, sql: str) -> str:
        return f"Executed: {sql}"

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    db = Database()
    await db.connect()
    try:
        yield {"db": db}
    finally:
        await db.disconnect()

mcp = FastMCP("My MCP Server", lifespan=app_lifespan)

@mcp.tool()
def run_query(sql: str, ctx: Context) -> str:
    """
    Execute an SQL query through the shared database connection.
    """
    db = ctx.request_context.lifespan_context["db"]
    return db.query(sql)
```
</details>

----

## 6. Async Concurrency

- **Always use `async def`** for I/O-bound or network-bound operations.  
- **Avoid blocking calls** in tools or resources. If blocking is necessary, use a thread pool (e.g., `asyncio.to_thread`).  
- **Use Python 3.13 improvements** (e.g., `asyncio.TaskGroup`) for running concurrent tasks:

<details>
<summary>Example</summary>

```python
import asyncio
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("ParallelOps")

@mcp.tool()
async def process_files(file_paths: list[str], ctx: Context) -> str:
    """
    Process multiple files in parallel using TaskGroup.
    """
    async def process_file(fp: str) -> str:
        ctx.info(f"Processing file: {fp}")
        await asyncio.sleep(0.1)  # Simulated I/O
        return f"Done: {fp}"

    results = []
    async with asyncio.TaskGroup() as tg:
        for fp in file_paths:
            tg.create_task(process_file(fp))
    return "All files processed."
```
</details>

----

## 7. Testing and Quality

1. **Use `pytest`** for testing.  
2. **Structure tests** to mirror your server modules (e.g., `test_tools.py`, `test_resources.py`).  
3. **Mock external dependencies** to keep tests fast and deterministic.  
4. **Use `pytest-asyncio`** for async tools/resources.  
5. **Integration tests**: Use the `mcp.client` or `mcp dev` to test end-to-end MCP interactions.

----

## 8. Logging and Observability

- **Use `ctx.info()`, `ctx.warning()`, `ctx.error()`** for emitting logs from within Tools.  
- **Avoid printing** directly in Tools/Resources. Instead, rely on the MCP logging APIs or standard Python logging if you need server-level logs.  
- **Add meaningful log messages** that help debugging without revealing sensitive data.

----

## 9. Security and Validation

- **Validate inputs** in Tools. If your tool expects specific data shapes, consider a Pydantic model or manual checks.  
- **Sanitize external data** before logging or returning it.  
- **Least Privilege**: Tools should only do what is necessary. For instance, limit file system access, or separate read-only from write tools.  
- **Use environment variables** or a secrets manager for credentials. Never hard-code secrets.

----

## 10. Additional Tips

- **Keep docstrings up to date**: Tools, Resources, and Prompts rely on them for discoverability by LLMs.  
- **Use descriptive resource URIs**: e.g., `stats://{object_id}` or `config://{section}`.  
- **Short, single-purpose Tools** are often easier for LLMs to understand than multi-step or multi-purpose Tools.  
- **Periodic Refactoring**: As your server grows, reorganize Tools, Resources, and Prompts to keep modules cohesive and maintainable.

----

### Example: Minimal Server

```python
# server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DemoServer")

@mcp.tool()
def hello(name: str) -> str:
    """
    Say hello to a user.

    Args:
        name: The user's name.

    Returns:
        A greeting message.
    """
    return f"Hello, {name}!"

@mcp.resource("company://info")
def company_info() -> dict[str, str]:
    """
    Provide static company information as a resource.
    """
    return {
        "name": "ExampleCorp",
        "location": "Remote",
    }

@mcp.prompt()
def greet_and_instruct() -> str:
    """
    Prompt template instructing the LLM how to greet and proceed.
    """
    return (
        "Use the 'hello' tool to greet the user, then ask them "
        "if they need any further assistance."
    )

if __name__ == "__main__":
    # Run the server in SSE mode
    mcp.run()
```

----

Following these guidelines will help ensure your MCP server is idiomatic, testable, and easy for LLMs to navigate. Happy coding!