# Getting Started with the Google ADK Test Application

This guide walks you through setting up your local environment, obtaining credentials, and preparing to run the Google ADK test application.

---

## 1. Prerequisites

Before running the application, ensure you have:

- **Python**: Version 3.10 or higher (`python3 --version`).
- **Git**: Installed and configured (`git --version`).
- **Google Gemini API Key**: A free or paid API key from [Google AI Studio](https://aistudio.google.com/).

---

## 2. Environment Setup

### 2.1 Clone or Navigate to the Workspace

```bash
cd /Users/noam/Documents/AI/test
```

### 2.2 Create and Activate a Virtual Environment

It is best practice to isolate project dependencies using a dedicated virtual environment:

```bash
# Create the virtual environment
python3 -m venv .venv

# Activate on macOS / Linux
source .venv/bin/activate
```

### 2.3 Configure Environment Variables

1. Copy the sample environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` and set your Google Gemini API key:
   ```env
   GOOGLE_API_KEY=AIzaSy...your_key_here
   ADK_MODEL=gemini-2.5-flash
   ```

---

## 3. Installing Dependencies

Once the implementation files are ready, install the required packages using `pip`:

```bash
# Core ADK framework and supporting libraries
pip install google-adk python-dotenv pytest
```

---

## 4. Execution Workflows (Once Implemented)

### Option A: Interactive Command-Line Interface (CLI)

Run the interactive terminal app:

```bash
python main.py
```

Example interaction:
```text
=== Google ADK Test Assistant ===
Type 'exit' to quit, 'clear' to reset session.

User: What is 45 * 18?
Agent: [Invoking tool 'calculate'] -> 45 * 18 = 810.

User: Check system diagnostics.
Agent: [Invoking tool 'get_system_info'] -> System health is nominal.
```

### Option B: Google ADK Web UI

Google ADK includes a built-in web-based developer console:

```bash
adk web app/agent.py
```

This launches a local web server (typically at `http://localhost:8080`) providing:
- An interactive chat interface.
- Live inspection of tool calls, inputs, and outputs.
- Execution traces and token metrics.

### Option C: ADK Direct CLI

You can also run agents directly using the ADK CLI:

```bash
adk run app/agent.py
```

---

## 5. Running Automated Tests

Run the test suite with `pytest`:

```bash
# Run all unit and integration tests
pytest tests/ -v

# Run with output capture disabled for debugging
pytest tests/ -s
```

---

## 6. Troubleshooting & FAQs

### Missing API Key
**Symptom**: `ValueError: GOOGLE_API_KEY is not set` or authentication error from Gemini API.  
**Resolution**: Verify that `.env` exists in the project root and contains a valid key. Ensure `python-dotenv` loads the file or export `export GOOGLE_API_KEY="your-key"` in your shell.

### Port Conflicts with `adk web`
**Symptom**: `OSError: [Errno 48] Address already in use`.  
**Resolution**: Specify an alternative port when launching the web UI:
```bash
adk web app/agent.py --port 8085
```

### Rate Limiting / Quotas
**Symptom**: HTTP 429 (Too Many Requests).  
**Resolution**: Check your project quota in Google AI Studio or switch to `gemini-1.5-flash` in `.env`.
