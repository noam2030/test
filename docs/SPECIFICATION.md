# Functional Specification: Google ADK Customer Support Agent

This document defines the functional requirements, tool interface contracts, mock data schemas, and test cases for **`customer_support_agent`**.

---

## 1. Persona & Objectives

The agent acts as **Nova**, a tier-1 customer support specialist for an e-commerce platform.
- **Tone**: Empathetic, concise, clear, and professional.
- **Core Directives**:
  - Always verify orders and accounts using appropriate tools rather than guessing.
  - Check return/refund eligibility using policy guidelines.
  - Escalate unresolved or complex issues by creating support tickets.
  - Maintain privacy by requesting only necessary identifiers.

---

## 2. Agent Configuration

| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Agent Name** | `customer_support_agent` | Identifier within Google ADK |
| **Model** | `gemini-2.5-flash` | Gemini model optimized for low latency and accurate tool calling |
| **Fallback Model** | `gemini-1.5-flash` | Configurable fallback |
| **Runner** | `InMemoryRunner` | Default session runner |

### System Instructions

```text
You are Nova, an AI Customer Support Specialist.
Your goal is to provide helpful, courteous, and efficient assistance.
Guidelines:
1. Greet the customer warmly and introduce yourself if not already done.
2. For order inquiries, use the `get_order_status` tool with the provided order ID.
3. For return or refund inquiries, use the `check_refund_policy` tool by specifying the item category and how many days have passed since purchase.
4. If a customer needs their account or order history looked up, use `get_customer_account`.
5. If an issue cannot be resolved, if the customer is dissatisfied, or if manual intervention is required, offer to create a formal support ticket using `create_support_ticket`.
6. Always communicate clearly, explaining results in plain language rather than raw JSON.
```

---

## 3. Tool Specifications

### 3.1 `get_order_status` (`app/tools/orders.py`)

#### Signature
```python
def get_order_status(order_id: str) -> dict[str, Any]:
    """Retrieves shipping status, tracking details, and items for an order.

    Args:
        order_id: The order identifier (e.g., 'ORD-1001', 'ORD-1002').

    Returns:
        dict containing order status, items, carrier, tracking number,
        estimated or actual delivery date, and eligibility details.
    """
```

#### Return Schema
```json
// Success
{
  "success": true,
  "order_id": "ORD-1001",
  "status": "In Transit",
  "carrier": "FedEx",
  "tracking_number": "TRK982341",
  "items": [{"name": "Wireless Noise-Cancelling Headphones", "category": "electronics", "qty": 1, "price": 149.99}],
  "estimated_delivery": "2026-09-25",
  "total": 149.99
}

// Error (Order not found)
{
  "success": false,
  "order_id": "ORD-9999",
  "error": "Order 'ORD-9999' was not found. Please verify the order number."
}
```

---

### 3.2 `check_refund_policy` (`app/tools/policies.py`)

#### Signature
```python
def check_refund_policy(item_category: str, days_since_purchase: int) -> dict[str, Any]:
    """Evaluates return and refund eligibility based on product category and purchase date.

    Args:
        item_category: Category of item ('electronics', 'apparel', 'books', 'perishables', 'software').
        days_since_purchase: Number of days since the item was delivered/purchased.

    Returns:
        dict containing eligibility flag, maximum allowable return window,
        conditions (e.g. original packaging), and restocking fees if applicable.
    """
```

#### Return Schema
```json
{
  "category": "electronics",
  "days_since_purchase": 14,
  "eligible": true,
  "max_days": 30,
  "requires_receipt": true,
  "conditions": "Must be in original box with all accessories included.",
  "restocking_fee": "0%"
}
```

---

### 3.3 `create_support_ticket` (`app/tools/tickets.py`)

#### Signature
```python
def create_support_ticket(customer_id: str, issue_summary: str, priority: str = "medium") -> dict[str, Any]:
    """Creates a new customer support escalation ticket.

    Args:
        customer_id: The customer ID or email address.
        issue_summary: Brief description of the unresolved issue.
        priority: Urgency level ('low', 'medium', 'high', 'urgent').

    Returns:
        dict with the created ticket ID, status, assigned team, and SLA response time.
    """
```

#### Return Schema
```json
{
  "success": true,
  "ticket_id": "TCK-4821",
  "customer_id": "CUST-501",
  "status": "Open",
  "priority": "medium",
  "assigned_team": "Tier 2 Support",
  "expected_response_time": "Within 24 hours",
  "message": "Ticket created successfully. A specialist will review your request."
}
```

---

### 3.4 `get_customer_account` (`app/tools/accounts.py`)

#### Signature
```python
def get_customer_account(email_or_id: str) -> dict[str, Any]:
    """Finds a customer account and returns profile details along with recent orders.

    Args:
        email_or_id: Customer email address or customer ID (e.g. 'CUST-501', 'alice@example.com').

    Returns:
        dict containing customer profile, loyalty tier, and list of associated order IDs.
    """
```

---

## 4. Built-in Mock Data

To enable immediate testing out of the box without requiring external database setup, the tools provide predefined mock records:

- **Customers**:
  - `CUST-501` / `alice@example.com`: Alice Smith (Gold Tier) - Orders: `ORD-1001`, `ORD-1002`
  - `CUST-502` / `bob@example.com`: Bob Jones (Silver Tier) - Orders: `ORD-1003`
- **Orders**:
  - `ORD-1001`: Wireless Headphones (`electronics`, $149.99), Status: `In Transit` (FedEx `TRK982341`, arriving in 3 days)
  - `ORD-1002`: Running Shoes (`apparel`, $89.50), Status: `Delivered` (10 days ago)
  - `ORD-1003`: Fresh Gourmet Fruit Basket (`perishables`, $45.00), Status: `Delivered` (2 days ago)
- **Policy Windows**:
  - `electronics`: 30 days
  - `apparel`: 45 days
  - `books`: 30 days
  - `perishables`: 0 days (non-returnable)
  - `software`: 14 days (unopened only)

---

## 5. Verification & Test Matrix

| Test ID | Category | User Query | Expected Action | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Greeting | "Hello, who are you?" | Direct answer | Introduces Nova, customer support specialist |
| **TC-02** | Order Status | "Where is my order ORD-1001?" | Calls `get_order_status` | Reports "In Transit via FedEx", estimated delivery date |
| **TC-03** | Missing Order | "What's the status of order ORD-9999?" | Calls `get_order_status` | Reports order not found, politely asks customer to double-check |
| **TC-04** | Return Policy | "Can I return shoes purchased 10 days ago?" | Calls `check_refund_policy` | Informs apparel has 45-day window, return is eligible |
| **TC-05** | Non-returnable | "Can I get a refund on a fruit basket delivered yesterday?" | Calls `check_refund_policy` | Explains perishables are non-returnable |
| **TC-06** | Ticket Escalation | "My package was damaged and I want to speak to a supervisor" | Calls `create_support_ticket` | Creates ticket (e.g. `TCK-XXXX`) and provides turnaround SLA |
| **TC-07** | Account Lookup | "Find my account for alice@example.com" | Calls `get_customer_account` | Greets Alice, mentions Gold tier and recent orders |
