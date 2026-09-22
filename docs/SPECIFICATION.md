# Functional Specification: Google ADK Test Application

This document defines the requirements, interface contracts, tool specifications, and test cases for the Google ADK test application.

---

## 1. Objectives

- Provide a clean, robust reference implementation of Google's Agent Development Kit (`google-adk`).
- Demonstrate agent configuration, custom function calling (tools), session handling, and programmatic execution.
- Establish a baseline testbed suitable for unit testing, interactive terminal debugging, and visual inspection via `adk web`.

---

## 2. Agent Definition

### 2.1 Configuration

| Parameter | Specification | Description |
| :--- | :--- | :--- |
| **Name** | `test_assistant` | Identifier for the agent instance within ADK |
| **Model** | `gemini-2.5-flash` | Gemini model optimized for speed, cost, and high-accuracy tool calling |
| **Fallback Model** | `gemini-1.5-flash` | Fallback option configurable via `.env` |
| **Runner Type** | `InMemoryRunner` | Default runtime runner for session memory management |

### 2.2 System Instructions (Prompt)

The agent will be instructed with the following system prompt:

```text
You are a knowledgeable and helpful AI assistant equipped with specialized tools.
Always evaluate user requests and determine if tools should be called:
1. For mathematical computations or arithmetic, use the `calculator` tool. Do not guess or estimate calculations.
2. For system diagnostics, runtime environment details, or health metrics, use the `get_system_info` tool.
3. If a question can be answered accurately without tools, respond clearly and concisely.
4. If a tool returns an error, explain the issue politely to the user and suggest corrections.
```

---

## 3. Tool Specifications

### 3.1 Calculator Tool (`app/tools/calculator.py`)

#### Function Signature
```python
def calculate(expression: str) -> dict[str, Any]:
    """Evaluates a mathematical expression safely.
    
    Args:
        expression: A string containing an arithmetic expression (e.g., '12 * (3 + 4)').
        
    Returns:
        A dictionary containing:
            - success (bool): True if evaluation succeeded, False otherwise.
            - result (float | int | None): The computed numerical result.
            - error (str | None): Error explanation if evaluation failed.
    """
```

#### Input Validation & Constraints
- Supports basic arithmetic operators: `+`, `-`, `*`, `/`, `**` (power), `//` (integer division), `%` (modulo), and parentheses.
- Parses expressions safely using Python's `ast` module (Abstract Syntax Tree) rather than unrestricted `eval()` to prevent arbitrary code execution.
- Gracefully handles division by zero (`ZeroDivisionError`) and syntax errors.

#### Output Example
```json
// Success
{
  "success": true,
  "expression": "25 * (4 + 6)",
  "result": 250,
  "error": null
}

// Error
{
  "success": false,
  "expression": "10 / 0",
  "result": null,
  "error": "Division by zero is not permitted."
}
```

---

### 3.2 System Diagnostics Tool (`app/tools/system_info.py`)

#### Function Signature
```python
def get_system_info(include_environment: bool = False) -> dict[str, Any]:
    """Retrieves diagnostic status, runtime information, and health metrics.
    
    Args:
        include_environment: Whether to include non-sensitive OS environment details.
        
    Returns:
        A dictionary containing timestamp, health status, Python runtime version,
        memory mock metrics, and platform details.
    """
```

#### Output Example
```json
{
  "status": "healthy",
  "timestamp": "2026-09-22T11:45:00Z",
  "python_version": "3.14.5",
  "framework": "google-adk",
  "environment": "development",
  "metrics": {
    "active_sessions": 1,
    "system_load": "nominal"
  }
}
```

---

## 4. Execution & CLI Specification (`main.py`)

### 4.1 CLI Commands & Options

When executing `python main.py`, the CLI should provide:

- **Interactive Mode (Default)**: Launches a continuous REPL session where the user can enter multi-turn queries.
- **Single-Shot Flag (`--prompt "<text>"`)**: Evaluates a single prompt, outputs the agent's response, and exits.
- **Session Control Commands**:
  - `exit` or `quit`: Terminate the CLI.
  - `clear`: Reset the current conversation session memory.
  - `help`: Display available commands and tool descriptions.

### 4.2 Terminal Output Formatting
- Clear role indicators (e.g. `User: `, `Agent: `).
- Optional verbose flag (`--verbose`) to display internal tool call invocations and their payloads for debugging.

---

## 5. Verification & Test Matrix

| Test Case ID | Scenario | Input Prompt | Expected Agent Action | Expected Result |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Knowledge Query | "What is the capital of France?" | No tool invoked | Accurate direct response ("Paris") |
| **TC-02** | Arithmetic | "What is 144 divided by 12 multiplied by 3?" | Invokes `calculate` tool | Correct calculation result (36) |
| **TC-03** | System Diagnostic | "Check the current system health and status" | Invokes `get_system_info` tool | Formatted report with status "healthy" |
| **TC-04** | Combined Multi-Tool | "Calculate 15 * 8 and report the system status" | Invokes both `calculate` and `get_system_info` | Answer contains both the computation (120) and status |
| **TC-05** | Tool Error Handling | "What is 100 divided by 0?" | Invokes `calculate` tool | Handles division by zero gracefully without crashing |
| **TC-06** | Session Continuity | Multi-turn prompt referencing prior answer | Memory lookup in session | Resolves context from earlier turn |
