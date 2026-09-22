"""Execution runner harness for the Google ADK Customer Support Agent."""

import asyncio
import os
from dataclasses import dataclass, field
from typing import Any

from google.adk.runners import Event, InMemoryRunner
from google.genai import types

from app.agent import root_agent


from app.security import default_agent_gateway, default_model_armor, SecurityAction


@dataclass
class AgentResponse:
    """Structured response from the agent containing text, tool calls, and telemetry."""

    text: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    session_id: str = ""
    user_id: str = ""
    security_flags: list[str] = field(default_factory=list)
    is_security_blocked: bool = False
    sanitized_prompt: str = ""


class CustomerSupportRunner:
    """High-level runner wrapping Google ADK's InMemoryRunner for customer support."""

    def __init__(self, agent=None):
        self.agent = agent or root_agent
        self.runner = InMemoryRunner(agent=self.agent)
        self.active_sessions: set[tuple[str, str]] = set()

    async def _ensure_session(self, user_id: str, session_id: str):
        """Ensures that a session is initialized in the session service."""
        key = (user_id, session_id)
        if key not in self.active_sessions:
            session = await self.runner.session_service.get_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=session_id,
            )
            if not session:
                await self.runner.session_service.create_session(
                    app_name=self.runner.app_name,
                    user_id=user_id,
                    session_id=session_id,
                )
            self.active_sessions.add(key)

    async def ask_async(
        self,
        prompt: str,
        user_id: str = "customer_1",
        session_id: str = "session_1",
    ) -> AgentResponse:
        """Sends a user prompt to the agent and collects the final response and tool invocations.

        Args:
            prompt: The user query or message.
            user_id: Unique user identifier for session isolation.
            session_id: Session identifier to maintain multi-turn context.

        Returns:
            AgentResponse containing the agent's synthesized response text and tool calls.
        """
        # 1. Inline Model Armor pre-screening
        armor_check = default_model_armor.sanitize_prompt(prompt)
        if armor_check.action == SecurityAction.BLOCK:
            refusal_text = (
                f"[Agent Gateway Security Refusal]\n"
                f"{armor_check.rejection_reason}\n"
                f"(Threat flags: {', '.join(armor_check.flags)})"
            )
            default_agent_gateway.log_event(
                stage="INGRESS_USER_PROMPT",
                result=armor_check,
                user_id=user_id,
                session_id=session_id,
            )
            return AgentResponse(
                text=refusal_text,
                session_id=session_id,
                user_id=user_id,
                security_flags=armor_check.flags,
                is_security_blocked=True,
                sanitized_prompt="",
            )

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key.startswith("your_gemini"):
            return AgentResponse(
                text=(
                    "[Configuration Notice] GOOGLE_API_KEY is not set or using placeholder.\n"
                    "To enable live Gemini responses, set a valid key in your `.env` file.\n"
                    "Example: GOOGLE_API_KEY=AIzaSy..."
                ),
                session_id=session_id,
                user_id=user_id,
                security_flags=armor_check.flags,
                sanitized_prompt=armor_check.sanitized_text,
            )

        await self._ensure_session(user_id, session_id)

        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=armor_check.sanitized_text)],
        )

        response_texts: list[str] = []
        tool_calls: list[dict[str, Any]] = []
        recorded_events: list[Event] = []

        try:
            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=user_content,
            ):
                recorded_events.append(event)

                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Extract text
                        if hasattr(part, "text") and part.text:
                            response_texts.append(part.text)

                        # Extract function calls (tool requests)
                        if hasattr(part, "function_call") and part.function_call:
                            fc = part.function_call
                            tool_calls.append(
                                {
                                    "type": "call",
                                    "name": getattr(fc, "name", "unknown"),
                                    "args": getattr(fc, "args", {}),
                                }
                            )

                        # Extract function responses (tool results)
                        if hasattr(part, "function_response") and part.function_response:
                            fr = part.function_response
                            tool_calls.append(
                                {
                                    "type": "response",
                                    "name": getattr(fr, "name", "unknown"),
                                    "response": getattr(fr, "response", {}),
                                }
                            )

            final_text = "".join(response_texts).strip()
            if not final_text and tool_calls:
                final_text = f"Tool execution completed: {len(tool_calls)} tool action(s) processed."

            return AgentResponse(
                text=final_text,
                tool_calls=tool_calls,
                events=recorded_events,
                session_id=session_id,
                user_id=user_id,
            )

        except Exception as e:
            return AgentResponse(
                text=f"An error occurred while communicating with the agent: {e}",
                tool_calls=tool_calls,
                events=recorded_events,
                session_id=session_id,
                user_id=user_id,
            )

    def ask_sync(
        self,
        prompt: str,
        user_id: str = "customer_1",
        session_id: str = "session_1",
    ) -> AgentResponse:
        """Synchronous wrapper around ask_async for convenience."""
        return asyncio.run(self.ask_async(prompt, user_id=user_id, session_id=session_id))

    async def clear_session(self, user_id: str, session_id: str) -> None:
        """Clears/deletes session state from memory."""
        try:
            await self.runner.session_service.delete_session(
                app_name=self.runner.app_name,
                user_id=user_id,
                session_id=session_id,
            )
            self.active_sessions.discard((user_id, session_id))
        except Exception:
            pass


# Global default runner instance
default_runner = CustomerSupportRunner()
