# Getting Started with the Customer Support Agent

This guide walks you through setting up your local environment, installing dependencies, configuring credentials, and running the **`customer_support_agent`** built with Google's Agent Development Kit (ADK).

---

## 1. Prerequisites

- **Python**: Version 3.10+ (`python3 --version`).
- **Git**: Installed and configured (`git --version`).
- **Google Gemini API Key**: From [Google AI Studio](https://aistudio.google.com/).

---

## 2. Environment Setup

### 2.1 Navigate to the Workspace
```bash
cd /Users/noam/Documents/AI/test
```

### 2.2 Create and Activate a Virtual Environment
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate on macOS / Linux
source .venv/bin/activate
```

### 2.3 Configure Environment Variables
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and configure your API key:
   ```env
   GOOGLE_API_KEY=AIzaSy...your_gemini_api_key_here
   ADK_MODEL=gemini-3.6-flash
   ```

---

## 3. Installing Dependencies

Install the required packages using the project `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 4. Running the Agent

### Option A: Interactive Customer Support CLI

Launch the interactive terminal console:

```bash
python main.py
```

Try asking sample support questions:
- *"Hi, I need help with my order."*
- *"What is the status of order ORD-1001?"*
- *"Can I return an apparel item purchased 10 days ago?"*
- *"Look up my account with email alice@example.com."*
- *"My package arrived damaged, please file a ticket."*

Commands:
- `exit` or `quit`: Exit the program.
- `clear`: Reset the current conversation session memory.
- `help`: Display available tools and sample queries.

### Option B: Google ADK Web UI

Google ADK provides a visual web playground for inspecting agent reasoning and tool executions:

```bash
adk web app/agent.py
```

Open `http://localhost:8080` in your browser to interact with Nova and inspect tool call payloads.

---

## 5. Running Automated Tests

Run the test suite using `pytest`:

```bash
# Run all tests
pytest tests/ -v

# Run only tool tests
pytest tests/test_tools.py -v
```

---

## 6. Built-in Test Data

You can immediately test the agent with these built-in test records:

- **Order IDs**:
  - `ORD-1001` (Wireless Headphones - In Transit via FedEx)
  - `ORD-1002` (Running Shoes - Delivered 10 days ago)
  - `ORD-1003` (Fruit Basket - Perishable, Delivered 2 days ago)
- **Customer Accounts**:
  - `CUST-501` / `alice@example.com` (Gold Tier)
  - `CUST-502` / `bob@example.com` (Silver Tier)
