"""Interactive Command-Line Interface for the Google ADK Customer Support Agent."""

import argparse
import sys
from dotenv import load_dotenv

from app.runner import CustomerSupportRunner
from app.tools.tickets import list_tickets

# Ensure .env is loaded
load_dotenv()


def print_banner():
    banner = """
========================================================================
     🎧 Nova - Google ADK Customer Support Agent
========================================================================
Type your inquiry below. Commands:
  • 'help'    - Show sample questions and available tools
  • 'tickets' - View all created support escalation tickets
  • 'clear'   - Reset conversation session memory
  • 'exit'    - Quit the application
========================================================================
"""
    print(banner)


def print_help():
    help_text = """
Available Customer Support Capabilities:
  1. Order Status:
     - "Where is my order ORD-1001?"
     - "Track shipment for ORD-1002"
  2. Return & Refund Policy:
     - "Can I return shoes purchased 10 days ago?"
     - "Can I get a refund for fresh fruit delivered 2 days ago?"
  3. Account Lookup:
     - "Look up my account for alice@example.com"
     - "What orders are on account CUST-502?"
  4. Ticket Escalation:
     - "My headphones arrived damaged, please file an urgent ticket"
     - "I want to speak with a human specialist"

Built-in Test Records:
  - Orders: ORD-1001 (In Transit), ORD-1002 (Delivered), ORD-1003 (Perishables)
  - Accounts: alice@example.com (Gold), bob@example.com (Silver)
"""
    print(help_text)


def print_tickets():
    tickets = list_tickets()
    if not tickets:
        print("\n[Tickets] No support tickets have been created yet.\n")
        return

    print(f"\n[Registered Support Tickets ({len(tickets)})]:")
    for t in tickets:
        print(
            f"  • {t['ticket_id']} | Priority: {t['priority'].upper()} | "
            f"Customer: {t['customer_id']} | Status: {t['status']}"
        )
        print(f"    Summary: {t['issue_summary']}")
        print(f"    Created: {t['created_at']} | Response SLA: {t['expected_response_time']}\n")


def run_interactive_loop(runner: CustomerSupportRunner, user_id: str, session_id: str, verbose: bool):
    print_banner()
    while True:
        try:
            user_input = input("\nCustomer > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in {"exit", "quit", "q"}:
            print("Thank you for contacting customer support. Have a great day!")
            break
        elif cmd == "help":
            print_help()
            continue
        elif cmd == "tickets":
            print_tickets()
            continue
        elif cmd == "clear":
            import asyncio
            asyncio.run(runner.clear_session(user_id, session_id))
            print("\n[Session] Conversation memory has been cleared.\n")
            continue

        print("\nNova is thinking...", end="\r", flush=True)
        response = runner.ask_sync(user_input, user_id=user_id, session_id=session_id)

        # Clear the "thinking..." line
        print(" " * 40, end="\r")

        if verbose and response.tool_calls:
            print("\n[Tool Actions Invoked]:")
            for action in response.tool_calls:
                if action["type"] == "call":
                    print(f"  ⚡ Calling tool '{action['name']}' with args: {action['args']}")
                elif action["type"] == "response":
                    print(f"  📥 Tool '{action['name']}' returned: {action['response']}")
            print("-" * 50)

        print(f"\nNova > {response.text}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Google ADK Customer Support Agent Terminal Interface"
    )
    parser.add_argument(
        "--prompt",
        "-p",
        type=str,
        help="Run a single prompt and exit directly without entering interactive mode.",
    )
    parser.add_argument(
        "--user-id",
        type=str,
        default="customer_1",
        help="User identifier for session state management (default: customer_1).",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default="support_session_1",
        help="Session identifier for multi-turn history (default: support_session_1).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose tool execution events.",
    )

    args = parser.parse_args()
    runner = CustomerSupportRunner()

    if args.prompt:
        response = runner.ask_sync(args.prompt, user_id=args.user_id, session_id=args.session_id)
        if args.verbose and response.tool_calls:
            print("[Tool Actions]:", response.tool_calls)
        print(response.text)
    else:
        run_interactive_loop(runner, args.user_id, args.session_id, args.verbose)


if __name__ == "__main__":
    main()
