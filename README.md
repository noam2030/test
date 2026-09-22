# Google ADK Test Application

A reference test application and experimental playground built with Google's **Agent Development Kit (ADK)** (`google-adk`).

This repository contains the architecture design, technical specifications, and setup documentation for an autonomous AI agent application leveraging Google Gemini and the ADK ecosystem.

---

## 📖 Overview

Google's **Agent Development Kit (ADK)** is an open-source, code-first framework designed for creating, evaluating, debugging, and deploying production-grade AI agents and multi-agent systems.

This project serves as a structured test application demonstrating:
1. **Agent Definition**: Configuring agent personality, instructions, and model selection with Gemini.
2. **Tool Integration**: Connecting custom Python functions, tool contexts, and external capability providers.
3. **Execution & Runtime**: Utilizing ADK's `Runner` architecture (`InMemoryRunner`) for state management and multi-turn conversations.
4. **Developer Interfaces**: Interacting with the agent via command-line interface (CLI) and the built-in ADK Web UI (`adk web`).

---

## 🗂️ Project Structure

```text
test/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore configuration
├── README.md                 # Project overview and high-level documentation
├── docs/
│   ├── ARCHITECTURE.md       # Technical architecture & Google ADK runtime concepts
│   ├── SPECIFICATION.md      # Functional specification of the test application
│   └── GETTING_STARTED.md    # Environment setup and developer guide
├── app/                      # [Planned] Application source code
│   ├── __init__.py
│   ├── agent.py              # Google ADK agent definition & system prompt
│   ├── runner.py             # Programmatic execution harness
│   └── tools/                # Custom agent tools
│       ├── __init__.py
│       ├── calculator.py     # Math & evaluation tool
│       └── system_info.py    # Environment & diagnostics tool
├── main.py                   # [Planned] Interactive CLI entry point
└── tests/                    # [Planned] Unit and integration tests
    ├── __init__.py
    └── test_agent.py         # Test suite for tools and agent workflows
```

---

## 📚 Documentation

Detailed documentation is organized in the [`docs/`](./docs) directory:

- **[System Architecture (`docs/ARCHITECTURE.md`)](./docs/ARCHITECTURE.md)**:
  - Deep-dive into Google ADK building blocks (`Agent`, `Runner`, `Tools`, `Session`).
  - Sequence diagrams and request lifecycle.
  - State management and tool calling flow.

- **[Application Specification (`docs/SPECIFICATION.md`)](./docs/SPECIFICATION.md)**:
  - Functional requirements for the test agent.
  - Tool schemas, input parameters, and output contracts.
  - Planned test scenarios and verification criteria.

- **[Getting Started (`docs/GETTING_STARTED.md`)](./docs/GETTING_STARTED.md)**:
  - Prerequisites (Python 3.10+, Gemini API Key).
  - Virtual environment and dependency installation.
  - Running options (CLI, Web UI, and automated tests).

---

## 🚀 Quick Reference (Planned Execution)

Once the application code is implemented, the workflow will be:

```bash
# 1. Clone & enter repository
git clone https://github.com/noam2030/test.git
cd test

# 2. Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install google-adk python-dotenv pytest

# 4. Configure environment
cp .env.example .env
# Add your Gemini API key in .env

# 5. Run the agent CLI
python main.py

# 6. Or launch the Google ADK Web UI
adk web app/agent.py
```

---

## 🔗 Repository Information

- **Remote URL**: [https://github.com/noam2030/test](https://github.com/noam2030/test)
- **Primary Branch**: `main`
- **Framework**: [Google Agent Development Kit (`google-adk`)](https://github.com/google/adk-python)
- **Model**: Google Gemini (via Google AI Studio or Vertex AI)
