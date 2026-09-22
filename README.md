# Google ADK Customer Support Agent

A production-ready reference customer support AI agent application built with Google's **Agent Development Kit (ADK)** (`google-adk`).

This application implements **`customer_support_agent`**, an intelligent e-commerce support assistant that resolves customer inquiries, checks order statuses, explains return/refund policies, and creates escalation support tickets using custom ADK tools and Google Gemini.

---

## 📖 Overview

Google's **Agent Development Kit (ADK)** is an open-source, code-first framework designed for creating, evaluating, debugging, and deploying production-grade AI agents and multi-agent systems.

The **Customer Support Agent** demonstrates:
1. **Agent Definition**: Configuring agent persona, system instructions, and model settings with Google Gemini (`gemini-2.5-flash`).
2. **Support Toolsets**: Connecting domain-specific customer support tools:
   - **Order Tracking**: Real-time status lookup and shipment tracking (`get_order_status`).
   - **Refund & Return Policy**: Policy evaluation based on item category and purchase age (`check_refund_policy`).
   - **Ticket Escalation**: Formal issue logging and escalation (`create_support_ticket`).
   - **Customer Account Lookup**: Profile details and active order retrieval (`get_customer_account`).
3. **Execution Runtime**: Utilizing ADK's `InMemoryRunner` for conversational multi-turn session state management.
4. **Developer Interfaces**: Interactive CLI (`main.py`), automated tests (`pytest`), and the Google ADK Web UI (`adk web`).

---

## 🗂️ Project Structure

```text
test/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules for venv, secrets, and caches
├── requirements.txt          # Python package dependencies
├── README.md                 # Project overview and documentation index
├── docs/
│   ├── ARCHITECTURE.md       # Technical architecture & Google ADK runtime concepts
│   ├── SPECIFICATION.md      # Functional specification of the customer_support_agent
│   └── GETTING_STARTED.md    # Environment setup and developer guide
├── app/
│   ├── __init__.py
│   ├── agent.py              # customer_support_agent definition & system prompt
│   ├── runner.py             # Programmatic execution runner using InMemoryRunner
│   └── tools/                # Support tool implementations
│       ├── __init__.py
│       ├── orders.py         # Order lookup and tracking tool
│       ├── policies.py       # Return and refund policy evaluator
│       ├── tickets.py        # Support ticket creation & escalation
│       └── accounts.py       # Customer profile & account lookup
├── main.py                   # Interactive CLI terminal interface
└── tests/
    ├── __init__.py
    ├── test_tools.py         # Unit tests for customer support tools
    └── test_agent.py         # Integration & configuration tests for the agent
```

---

## 📚 Documentation

- **[System Architecture (`docs/ARCHITECTURE.md`)](./docs/ARCHITECTURE.md)**:
  - Google ADK building blocks (`Agent`, `Runner`, `Tools`, `Session`).
  - Sequence diagrams for customer support multi-turn workflows and tool calling.
  - State management and error handling.

- **[Application Specification (`docs/SPECIFICATION.md`)](./docs/SPECIFICATION.md)**:
  - Full persona, role definition, and system prompt for `customer_support_agent`.
  - Tool schemas, input parameters, JSON responses, and error conditions.
  - Test matrix with sample queries (order status, refund checks, ticket creation).

- **[Getting Started (`docs/GETTING_STARTED.md`)](./docs/GETTING_STARTED.md)**:
  - Step-by-step setup guide (`.venv`, `requirements.txt`).
  - Google Gemini API key configuration.
  - Running via CLI (`python main.py`), ADK Web UI (`adk web`), or `pytest`.

---

## 🚀 Quick Start

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your GOOGLE_API_KEY

# 4. Run the interactive customer support CLI
python main.py

# 5. Or launch the Google ADK Web UI
adk web app/agent.py
```

---

## 🔗 Repository Information

- **Remote URL**: [https://github.com/noam2030/test](https://github.com/noam2030/test)
- **Agent Name**: `customer_support_agent`
- **Framework**: [Google Agent Development Kit (`google-adk`)](https://github.com/google/adk-python)
- **Model**: Google Gemini (`gemini-2.5-flash` or `gemini-1.5-flash`)
