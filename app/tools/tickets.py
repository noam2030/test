"""Support ticket creation and escalation tool for the Customer Support Agent."""

import time
from typing import Any

# In-memory ticket registry for tracking escalated cases
TICKETS_DB: list[dict[str, Any]] = []


def create_support_ticket(
    customer_id: str,
    issue_summary: str,
    priority: str = "medium",
) -> dict[str, Any]:
    """Creates a new support ticket and escalates complex or unresolved issues to human specialists.

    Args:
        customer_id: Identifier of the customer (e.g. 'CUST-501' or customer email).
        issue_summary: Concise description of the issue or customer request.
        priority: Priority level ('low', 'medium', 'high', 'urgent'). Default is 'medium'.

    Returns:
        dict containing the generated ticket ID, status, SLA response time, and confirmation details.
    """
    clean_priority = priority.strip().lower()
    if clean_priority not in {"low", "medium", "high", "urgent"}:
        clean_priority = "medium"

    ticket_num = len(TICKETS_DB) + 5001
    ticket_id = f"TCK-{ticket_num}"

    sla_map = {
        "urgent": "Within 2 hours",
        "high": "Within 6 hours",
        "medium": "Within 24 hours",
        "low": "Within 48 hours",
    }

    ticket = {
        "ticket_id": ticket_id,
        "customer_id": customer_id.strip(),
        "issue_summary": issue_summary.strip(),
        "priority": clean_priority,
        "status": "Open",
        "assigned_team": "Tier 2 Customer Support",
        "expected_response_time": sla_map[clean_priority],
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }

    TICKETS_DB.append(ticket)

    return {
        "success": True,
        "ticket_id": ticket["ticket_id"],
        "customer_id": ticket["customer_id"],
        "priority": ticket["priority"],
        "status": ticket["status"],
        "assigned_team": ticket["assigned_team"],
        "expected_response_time": ticket["expected_response_time"],
        "confirmation": (
            f"Support ticket {ticket_id} has been created successfully. "
            f"A representative from {ticket['assigned_team']} will respond {ticket['expected_response_time']}."
        ),
    }


def list_tickets() -> list[dict[str, Any]]:
    """Helper function to list all registered tickets (useful for debugging and testing)."""
    return list(TICKETS_DB)
