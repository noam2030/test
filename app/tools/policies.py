"""Return and refund policy evaluation tool for the Customer Support Agent."""

from typing import Any

POLICY_RULES: dict[str, dict[str, Any]] = {
    "electronics": {
        "max_days": 30,
        "conditions": "Must be in original packaging with all included accessories and serial numbers intact.",
        "restocking_fee": "0%",
        "requires_receipt": True,
    },
    "apparel": {
        "max_days": 45,
        "conditions": "Must be unworn, unwashed, and have original tags attached.",
        "restocking_fee": "0%",
        "requires_receipt": True,
    },
    "books": {
        "max_days": 30,
        "conditions": "Must be in like-new condition without markings or damaged spine.",
        "restocking_fee": "0%",
        "requires_receipt": True,
    },
    "perishables": {
        "max_days": 0,
        "conditions": "Perishable goods (e.g., fresh fruit, food items) are non-returnable and final sale.",
        "restocking_fee": "N/A",
        "requires_receipt": False,
    },
    "software": {
        "max_days": 14,
        "conditions": "Physical media must be unopened with unbroken seal. Digital keys are non-refundable once redeemed.",
        "restocking_fee": "15%",
        "requires_receipt": True,
    },
}

DEFAULT_POLICY = {
    "max_days": 30,
    "conditions": "Item must be in unused, resalable condition with original proof of purchase.",
    "restocking_fee": "0%",
    "requires_receipt": True,
}


def check_refund_policy(item_category: str, days_since_purchase: int) -> dict[str, Any]:
    """Evaluates return and refund eligibility based on item category and days since delivery/purchase.

    Args:
        item_category: Category of item ('electronics', 'apparel', 'books', 'perishables', 'software', or general).
        days_since_purchase: Number of days since the item was purchased or delivered.

    Returns:
        dict containing eligibility status, return window, requirements, and policy explanation.
    """
    category_key = item_category.strip().lower()
    policy = POLICY_RULES.get(category_key, DEFAULT_POLICY)

    max_days = policy["max_days"]
    if max_days == 0:
        eligible = False
        message = f"Items in the '{item_category}' category are perishable, non-returnable, and final-sale."
    elif days_since_purchase <= max_days:
        eligible = True
        remaining = max_days - days_since_purchase
        message = f"Item is eligible for return! You have {remaining} day(s) remaining in the {max_days}-day return window."
    else:
        eligible = False
        overdue = days_since_purchase - max_days
        message = (
            f"The {max_days}-day return window for '{item_category}' expired {overdue} day(s) ago."
        )

    return {
        "category": item_category,
        "days_since_purchase": days_since_purchase,
        "eligible": eligible,
        "max_return_days": max_days,
        "conditions": policy["conditions"],
        "restocking_fee": policy["restocking_fee"],
        "requires_receipt": policy["requires_receipt"],
        "policy_message": message,
    }
