# System Architecture: Google ADK Customer Support Agent

This document outlines the architecture, components, data flows, and runtime mechanics of the **`customer_support_agent`** application built with Google's **Agent Development Kit (ADK)**.

---

## 1. System Architecture

The `customer_support_agent` acts as an automated, empathic front-line support assistant. It uses Google ADK to process customer queries, maintain conversation state, invoke domain-specific tools, and formulate helpful, grounded responses.

```mermaid
flowchart TD
    User([Customer / User]) --> Interface[CLI REPL / Web UI / REST Endpoint]
    Interface --> Runner[Google ADK Runner\nInMemoryRunner]
    
    subgraph ADK Core Engine
        Runner --> SessionMgr[(Session & History Store)]
        Runner --> Agent[customer_support_agent\nInstructions + Model Config]
        Agent <--> LLM[Gemini Model\ne.g., gemini-3.6-flash]
        Agent <--> ToolRegistry[ADK Toolset Registry]
    end

    subgraph Customer Support Domain Tools
        ToolRegistry --> T1[get_order_status\nTrack shipping & delivery]
        ToolRegistry --> T2[check_refund_policy\nEvaluate return eligibility]
        ToolRegistry --> T3[create_support_ticket\nEscalate complex issues]
        ToolRegistry --> T4[get_customer_account\nLookup profile & orders]
    end

    T1 --> MockDB[(Mock Customer & Order Store)]
    T2 --> MockDB
    T3 --> MockDB
    T4 --> MockDB
```

---

## 2. Core Components

### 2.1 The Agent (`google.adk.agents.Agent`)
- **Identifier**: `customer_support_agent`
- **Model**: Default `gemini-3.6-flash` (or `gemini-1.5-flash`)
- **System Instructions**: Configured with customer service guidelines: polite tone, factual precision, mandatory tool verification for account/order inquiries, and standard escalation procedures when unable to resolve an issue directly.

### 2.2 Domain Toolsets (`app/tools/`)
ADK exposes Python functions directly to Gemini as callable tools:

1. **`get_order_status(order_id: str)`**:
   - Queries tracking details, carrier status, expected delivery date, and order items.
2. **`check_refund_policy(item_category: str, days_since_purchase: int)`**:
   - Evaluates eligibility according to policy rules (e.g., 30 days for electronics, 45 days for apparel, non-returnable final sale items).
3. **`create_support_ticket(customer_id: str, issue_summary: str, priority: str)`**:
   - Formally generates a support ticket for human representative review when automated resolution is impossible.
4. **`get_customer_account(email_or_id: str)`**:
   - Fetches customer account information, membership tier, and recent order history.

### 2.3 Runner & Session Management (`google.adk.runners.InMemoryRunner`)
- Manages multi-turn conversations where previous answers, customer IDs, or order numbers remain accessible in conversation memory.
- Orchestrates the tool invocation loop:
  1. User asks a question.
  2. Model detects need for tools and outputs `FunctionCall`.
  3. ADK Runner executes the tool locally.
  4. Tool output is injected as `FunctionResponse`.
  5. Model synthesizes the final customer-facing reply.

---

## 3. Interaction Sequence Diagram

Below is the workflow for a customer inquiring about an order's return eligibility:

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Customer
    participant CLI as main.py / CLI
    participant Runner as ADK InMemoryRunner
    participant Agent as customer_support_agent
    participant LLM as Gemini Model
    participant Tools as Support Tools

    Customer->>CLI: "Can I return my order ORD-1002?"
    CLI->>Runner: Send Prompt to active Session
    Runner->>Agent: Prepare Context & History
    Agent->>LLM: Send Instructions, History, Tools, Prompt
    
    LLM-->>Agent: FunctionCall: `get_order_status(order_id="ORD-1002")`
    Agent->>Tools: Execute `get_order_status("ORD-1002")`
    Tools-->>Agent: {"status": "delivered", "delivered_days_ago": 12, "category": "electronics"}
    
    Agent->>LLM: FunctionResponse: {"status": "delivered", "delivered_days_ago": 12, "category": "electronics"}
    LLM-->>Agent: FunctionCall: `check_refund_policy(item_category="electronics", days_since_purchase=12)`
    Agent->>Tools: Execute `check_refund_policy("electronics", 12)`
    Tools-->>Agent: {"eligible": true, "max_allowed_days": 30, "condition_notes": "Original packaging required"}
    
    Agent->>LLM: FunctionResponse: {"eligible": true, "max_allowed_days": 30}
    LLM-->>Agent: "Yes, you can return order ORD-1002! Electronics can be returned within 30 days..."
    Agent-->>Runner: Package response
    Runner-->>CLI: Deliver response to customer
    CLI-->>Customer: Render response
```

---

## 4. Resilience & Error Handling

- **Invalid Order/Account IDs**: Tools return clear structured error dictionaries (`{"success": false, "error": "Order not found"}`) allowing the agent to guide the user to verify their ID.
- **Graceful Escalation**: If a customer is dissatisfied or an unexpected exception occurs, the agent proactively offers to call `create_support_ticket`.
- **API Key Security**: Sensitive credentials stay in `.env` and are never logged or exposed in prompts.
