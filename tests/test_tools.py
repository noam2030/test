"""Unit tests for the Customer Support Agent domain tools."""

import pytest
from app.tools.accounts import get_customer_account
from app.tools.orders import get_order_status
from app.tools.policies import check_refund_policy
from app.tools.tickets import create_support_ticket, list_tickets


class TestOrderTool:
    def test_get_order_status_success(self):
        result = get_order_status("ORD-1001")
        assert result["success"] is True
        assert result["order_id"] == "ORD-1001"
        assert result["status"] == "In Transit"
        assert result["carrier"] == "FedEx"
        assert len(result["items"]) == 1
        assert result["items"][0]["category"] == "electronics"

    def test_get_order_status_delivered(self):
        result = get_order_status("ord-1002")  # Test case insensitivity
        assert result["success"] is True
        assert result["order_id"] == "ORD-1002"
        assert result["status"] == "Delivered"

    def test_get_order_status_not_found(self):
        result = get_order_status("ORD-9999")
        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestPolicyTool:
    def test_electronics_within_window(self):
        result = check_refund_policy("electronics", days_since_purchase=15)
        assert result["eligible"] is True
        assert result["max_return_days"] == 30
        assert "original packaging" in result["conditions"].lower()

    def test_electronics_past_window(self):
        result = check_refund_policy("electronics", days_since_purchase=35)
        assert result["eligible"] is False
        assert "expired" in result["policy_message"].lower()

    def test_apparel_extended_window(self):
        result = check_refund_policy("apparel", days_since_purchase=40)
        assert result["eligible"] is True
        assert result["max_return_days"] == 45

    def test_perishables_non_returnable(self):
        result = check_refund_policy("perishables", days_since_purchase=1)
        assert result["eligible"] is False
        assert result["max_return_days"] == 0
        assert "non-returnable" in result["policy_message"].lower()

    def test_software_policy(self):
        result = check_refund_policy("software", days_since_purchase=10)
        assert result["eligible"] is True
        assert result["restocking_fee"] == "15%"


class TestTicketTool:
    def test_create_ticket_standard(self):
        initial_count = len(list_tickets())
        result = create_support_ticket(
            customer_id="CUST-501",
            issue_summary="Package arrived with minor scuff",
            priority="medium",
        )
        assert result["success"] is True
        assert result["ticket_id"].startswith("TCK-")
        assert result["status"] == "Open"
        assert result["expected_response_time"] == "Within 24 hours"
        assert len(list_tickets()) == initial_count + 1

    def test_create_ticket_urgent_sla(self):
        result = create_support_ticket(
            customer_id="alice@example.com",
            issue_summary="Urgent: completely missing shipment",
            priority="urgent",
        )
        assert result["success"] is True
        assert result["priority"] == "urgent"
        assert result["expected_response_time"] == "Within 2 hours"


class TestAccountTool:
    def test_get_account_by_id(self):
        result = get_customer_account("CUST-501")
        assert result["success"] is True
        assert result["name"] == "Alice Smith"
        assert result["membership_tier"] == "Gold"
        assert "ORD-1001" in result["recent_orders"]

    def test_get_account_by_email(self):
        result = get_customer_account("bob@example.com")
        assert result["success"] is True
        assert result["name"] == "Bob Jones"
        assert result["membership_tier"] == "Silver"

    def test_get_account_not_found(self):
        result = get_customer_account("unknown@example.com")
        assert result["success"] is False
        assert "No customer account found" in result["error"]
