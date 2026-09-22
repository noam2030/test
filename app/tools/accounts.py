"""Customer account and profile lookup tool for the Customer Support Agent."""

from typing import Any

# Mock customer database
CUSTOMERS_DB: dict[str, dict[str, Any]] = {
    "CUST-501": {
        "customer_id": "CUST-501",
        "name": "Alice Smith",
        "email": "alice@example.com",
        "membership_tier": "Gold",
        "member_since": "2023-04-15",
        "orders": ["ORD-1001", "ORD-1002"],
    },
    "CUST-502": {
        "customer_id": "CUST-502",
        "name": "Bob Jones",
        "email": "bob@example.com",
        "membership_tier": "Silver",
        "member_since": "2024-01-20",
        "orders": ["ORD-1003"],
    },
}


def get_customer_account(email_or_id: str) -> dict[str, Any]:
    """Retrieves customer profile, loyalty tier, and associated order history.

    Args:
        email_or_id: The customer ID (e.g., 'CUST-501') or email address ('alice@example.com').

    Returns:
        dict containing the customer's profile and order references,
        or an error message if the customer account does not exist.
    """
    query = email_or_id.strip().lower()

    # Search by ID or email
    matched_customer = None
    for cust in CUSTOMERS_DB.values():
        if cust["customer_id"].lower() == query or cust["email"].lower() == query:
            matched_customer = cust
            break

    if not matched_customer:
        return {
            "success": False,
            "query": email_or_id,
            "error": f"No customer account found matching '{email_or_id}'. Please check the email or ID.",
        }

    return {
        "success": True,
        "customer_id": matched_customer["customer_id"],
        "name": matched_customer["name"],
        "email": matched_customer["email"],
        "membership_tier": matched_customer["membership_tier"],
        "member_since": matched_customer["member_since"],
        "recent_orders": matched_customer["orders"],
    }
