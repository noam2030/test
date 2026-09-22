"""Agent Gateway: Ingress and Egress security mediation layer using Model Armor."""

import time
from dataclasses import dataclass, field
from typing import Any

from google.adk.agents.context import Context
from google.genai import types

from app.security.model_armor import ModelArmor, SanitizationResult, SecurityAction, default_model_armor


@dataclass
class SecurityAuditEvent:
    """Audit record capturing a security interception or sanitization event."""

    timestamp: str
    stage: str  # INGRESS_USER_PROMPT, EGRESS_AGENT_RESPONSE, TOOL_CALL
    action: str  # ALLOW, SANITIZE, BLOCK
    threat_level: str
    flags: list[str]
    details: str
    user_id: str | None = None
    session_id: str | None = None


class AgentGateway:
    """Centralized security gateway mediating traffic between clients, Google ADK agents, and tools."""

    def __init__(self, armor: ModelArmor | None = None):
        self.armor = armor or default_model_armor
        self.audit_log: list[SecurityAuditEvent] = []

    def log_event(
        self,
        stage: str,
        result: SanitizationResult,
        user_id: str | None = None,
        session_id: str | None = None,
        extra_details: str = "",
    ):
        """Records a security audit entry."""
        event = SecurityAuditEvent(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            stage=stage,
            action=result.action.value,
            threat_level=result.threat_level,
            flags=list(result.flags),
            details=result.rejection_reason or extra_details or f"Action: {result.action.value}",
            user_id=user_id,
            session_id=session_id,
        )
        self.audit_log.append(event)

    def before_agent_guard(self, ctx: Context) -> types.Content | None:
        """Native Google ADK before_agent_callback hook.

        Inspects the incoming user message using Model Armor.
        - If malicious (jailbreak, prompt injection), immediately blocks execution and returns
          a security refusal without contacting the LLM.
        - If sensitive data (PII) is present, masks it in-place and lets the agent proceed.
        """
        user_content = ctx.user_content
        if not user_content or not user_content.parts:
            return None

        # Extract text from user content
        full_text = "".join(
            part.text for part in user_content.parts if hasattr(part, "text") and part.text
        )

        if not full_text:
            return None

        user_id = getattr(ctx, "user_id", None)
        session_id = getattr(ctx.session, "id", None) if hasattr(ctx, "session") else None

        result = self.armor.sanitize_prompt(full_text)
        self.log_event(
            stage="INGRESS_USER_PROMPT",
            result=result,
            user_id=user_id,
            session_id=session_id,
        )

        # 1. Threat detected: short-circuit and block turn
        if result.action == SecurityAction.BLOCK:
            refusal_message = (
                f"[Agent Gateway Security Refusal]\n"
                f"{result.rejection_reason}\n"
                f"(Threat flags: {', '.join(result.flags)})"
            )
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text=refusal_message)],
            )

        # 2. PII detected: sanitize user_content in-place and continue
        if result.action == SecurityAction.SANITIZE:
            # Replace parts with sanitized text
            ctx.user_content.parts = [types.Part.from_text(text=result.sanitized_text)]

        # Allow execution to proceed
        return None

    def after_agent_guard(self, ctx: Context) -> types.Content | None:
        """Native Google ADK after_agent_callback hook.

        Inspects outgoing agent response to prevent system prompt leakage or accidental secret disclosure.
        """
        user_id = getattr(ctx, "user_id", None)
        session_id = getattr(ctx.session, "id", None) if hasattr(ctx, "session") else None

        # Inspect any text generated in this turn
        if not hasattr(ctx, "output") or not ctx.output:
            return None

        raw_output = str(ctx.output)
        result = self.armor.sanitize_response(raw_output)

        if result.action == SecurityAction.SANITIZE:
            self.log_event(
                stage="EGRESS_AGENT_RESPONSE",
                result=result,
                user_id=user_id,
                session_id=session_id,
                extra_details="Sensitive data masked in model response.",
            )
            return types.Content(
                role="model",
                parts=[types.Part.from_text(text=result.sanitized_text)],
            )

        return None

    def before_tool_guard(self, tool: Any, args: dict[str, Any], ctx: Context) -> dict[str, Any] | None:
        """Native Google ADK before_tool_callback hook.

        Validates and sanitizes parameters passed to tools.
        """
        sanitized_args = {}
        has_changes = False

        for k, v in args.items():
            if isinstance(v, str):
                res = self.armor.sanitize_prompt(v)
                if res.action == SecurityAction.BLOCK:
                    # Sanitize to empty string or safe placeholder
                    sanitized_args[k] = "[UNSAFE_PARAMETER_REMOVED]"
                    has_changes = True
                elif res.action == SecurityAction.SANITIZE:
                    sanitized_args[k] = res.sanitized_text
                    has_changes = True
                else:
                    sanitized_args[k] = v
            else:
                sanitized_args[k] = v

        if has_changes:
            return sanitized_args
        return None

    def get_audit_log(self) -> list[SecurityAuditEvent]:
        """Returns the accumulated security audit log."""
        return list(self.audit_log)


# Global default gateway instance
default_agent_gateway = AgentGateway()
