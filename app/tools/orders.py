"""Order lookup and tracking tool for the Customer Support Agent."""

from typing import Any

# Mock order database for demonstration and testing
ORDERS_DB: dict[str, dict[str, Any]] = {
    "ORD-1001": {
        "order_id": "ORD-1001",
        "customer_id": "CUST-501",
        "status": "In Transit",
        "carrier": "FedEx",
        "tracking_number": "TRK982341",
        "estimated_delivery": "in 3 days",
        "days_since_purchase": 2,
        "items": [
            {
                "name": "Wireless Noise-Cancelling Headphones",
                "category": "electronics",
                "quantity": 1,
                "price": 149.99,
            }
        ],
        "total": 149.99,
    },
    "ORD-1002": {
        "order_id": "ORD-1002",
        "customer_id": "CUST-501",
        "status": "Delivered",
        "carrier": "UPS",
        "tracking_number": "TRK110482",
        "delivered_date": "10 days ago",
        "days_since_purchase": 10,
        "items": [
            {
                "name": "Performance Running Shoes",
                "category": "apparel",
                "quantity": 1,
                "price": 89.50,
            }
        ],
        "total": 89.50,
    },
    "ORD-1003": {
        "order_id": "ORD-1003",
        "customer_id": "CUST-502",
        "status": "Delivered",
        "carrier": "DHL",
        "tracking_number": "TRK772910",
        "delivered_date": "2 days ago",
        "days_since_purchase": 2,
        "items": [
            {
                "name": "Fresh Gourmet Fruit Basket",
                "category": "perishables",
                "quantity": 1,
                "price": 45.00,
            }
        ],
        "total": 45.00,
    },
}


def get_order_status(order_id: str) -> dict[str, Any]:
    """Retrieves current tracking status, shipment details, and items for an order.

    Args:
        order_id: The order identifier (e.g., 'ORD-1001', 'ORD-1002').

    Returns:
        dict containing order status, items, carrier, and delivery details,
        or an error message if the order is not found.
    """
    clean_id = order_id.strip().upper()
    order = ORDERS_DB.get(clean_id)

    if not order:
        return {
            "success": False,
            "order_id": clean_id,
            "error": f"Order '{clean_id}' was not found. Please verify the order number and try again.",
        }

    return {
        "success": True,
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "status": order["status"],
        "carrier": order["carrier"],
        "tracking_number": order["tracking_number"],
        "estimated_delivery": order.get("estimated_delivery") or order.get("delivered_date"),
        "days_since_purchase": order["days_since_purchase"],
        "items": order["items"],
        "total": order["total"],
    }
