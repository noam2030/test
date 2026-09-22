"""Model Armor security engine for prompt sanitization, jailbreak defense, and PII masking."""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SecurityAction(str, Enum):
    ALLOW = "ALLOW"
    SANITIZE = "SANITIZE"
    BLOCK = "BLOCK"


@dataclass
class SanitizationResult:
    """Result of a Model Armor security inspection."""

    action: SecurityAction
    original_text: str
    sanitized_text: str
    flags: list[str] = field(default_factory=list)
    threat_level: str = "NONE"  # NONE, LOW, MEDIUM, HIGH
    redacted_items: dict[str, int] = field(default_factory=dict)
    rejection_reason: str | None = None


class ModelArmor:
    """Inline security engine providing defense against prompt injection, jailbreaking, and PII leakage."""

    # Prompt injection and jailbreak heuristic patterns
    INJECTION_PATTERNS = [
        (
            r"(?i)\bignore\s+(all\s+|any\s+|the\s+)?(previous|prior|above|former)\s+(instructions|prompts|rules|commands|constraints)\b",
            "PROMPT_INJECTION_OVERRIDE",
            "HIGH",
        ),
        (
            r"(?i)\b(disregard|forget|override|bypass)\s+(all\s+)?(previous|prior|safety|system)\s+(rules|guidelines|instructions|filters)\b",
            "PROMPT_INJECTION_DISREGARD",
            "HIGH",
        ),
        (
            r"(?i)\b(reveal|output|print|show|repeat|display)\s+(your\s+)?(system\s+prompt|initial\s+instructions|internal\s+instructions|developer\s+prompt)\b",
            "SYSTEM_PROMPT_EXTRACTION",
            "HIGH",
        ),
        (
            r"(?i)\b(you\s+are\s+now\s+in|enable)\s+(developer\s+mode|dan\s+mode|unfiltered\s+mode|god\s+mode|evil\s+twin|jailbreak)\b",
            "JAILBREAK_ROLEPLAY_MODE",
            "HIGH",
        ),
        (
            r"(?i)\b(act\s+as|pretend\s+to\s+be)\s+an?\s+(unfiltered|unconstrained|jailbroken|evil)\s+(ai|assistant|model)\b",
            "JAILBREAK_UNFILTERED_PERSONA",
            "HIGH",
        ),
        (
            r"(?i)\[\s*system\s*:\s*override\s*\]|\[\s*developer\s*mode\s*:\s*active\s*\]",
            "PROMPT_INJECTION_DELIMITER_ATTACK",
            "HIGH",
        ),
    ]

    # PII and sensitive data patterns
    PII_PATTERNS = [
        # Credit Card Numbers (13 to 16 digits, with optional spaces or dashes)
        (
            r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b",
            "[REDACTED_CREDIT_CARD]",
            "CREDIT_CARD",
        ),
        (
            r"\b(?:\d{4}[ -]){3}\d{4}\b",
            "[REDACTED_CREDIT_CARD]",
            "CREDIT_CARD",
        ),
        # US Social Security Number (SSN)
        (
            r"\b\d{3}-\d{2}-\d{4}\b",
            "[REDACTED_SSN]",
            "SSN",
        ),
        # Google API Key Pattern
        (
            r"\bAIza[0-9A-Za-z-_]{35}\b",
            "[REDACTED_API_KEY]",
            "API_KEY",
        ),
        # Generic Secret / Bearer Token
        (
            r"(?i)\b(bearer\s+[a-zA-Z0-9_\-\.]{20,})\b",
            "[REDACTED_BEARER_TOKEN]",
            "AUTH_TOKEN",
        ),
    ]

    def __init__(self, block_injections: bool = True, redact_pii: bool = True):
        self.block_injections = block_injections
        self.redact_pii = redact_pii

    def sanitize_prompt(self, text: str) -> SanitizationResult:
        """Inspects and sanitizes an incoming user prompt before it reaches the agent or model.

        Args:
            text: Raw input prompt string from the user.

        Returns:
            SanitizationResult with action (ALLOW, SANITIZE, or BLOCK), sanitized text, and security flags.
        """
        if not text or not text.strip():
            return SanitizationResult(
                action=SecurityAction.ALLOW,
                original_text=text,
                sanitized_text=text,
            )

        flags: list[str] = []
        threat_level = "NONE"
        rejection_reason = None

        # 1. Check for Prompt Injection & Jailbreak Attacks
        if self.block_injections:
            for pattern, flag_name, severity in self.INJECTION_PATTERNS:
                if re.search(pattern, text):
                    flags.append(flag_name)
                    threat_level = severity
                    rejection_reason = (
                        "The submitted request violates security safety policies (potential "
                        f"{flag_name.replace('_', ' ').title()}). "
                        "Please ask a valid customer support question."
                    )
                    return SanitizationResult(
                        action=SecurityAction.BLOCK,
                        original_text=text,
                        sanitized_text="",
                        flags=flags,
                        threat_level=threat_level,
                        rejection_reason=rejection_reason,
                    )

        # 2. Check and Redact Sensitive PII
        sanitized_text = text
        redacted_items: dict[str, int] = {}

        if self.redact_pii:
            for pattern, replacement, item_type in self.PII_PATTERNS:
                matches = re.findall(pattern, sanitized_text)
                if matches:
                    count = len(matches)
                    redacted_items[item_type] = redacted_items.get(item_type, 0) + count
                    flags.append(f"PII_REDACTED_{item_type}")
                    sanitized_text = re.sub(pattern, replacement, sanitized_text)
                    if threat_level == "NONE":
                        threat_level = "LOW"

        action = SecurityAction.SANITIZE if redacted_items else SecurityAction.ALLOW

        return SanitizationResult(
            action=action,
            original_text=text,
            sanitized_text=sanitized_text,
            flags=flags,
            threat_level=threat_level,
            redacted_items=redacted_items,
        )

    def sanitize_response(self, text: str) -> SanitizationResult:
        """Inspects model egress responses to prevent internal instruction leaks or credential exposure.

        Args:
            text: Raw response string from the agent or model.

        Returns:
            SanitizationResult with any leaked secrets masked.
        """
        if not text:
            return SanitizationResult(
                action=SecurityAction.ALLOW,
                original_text=text,
                sanitized_text=text,
            )

        flags: list[str] = []
        sanitized_text = text
        redacted_items: dict[str, int] = {}
        threat_level = "NONE"

        # Check for API Keys in output
        for pattern, replacement, item_type in self.PII_PATTERNS:
            matches = re.findall(pattern, sanitized_text)
            if matches:
                count = len(matches)
                redacted_items[item_type] = redacted_items.get(item_type, 0) + count
                flags.append(f"EGRESS_LEAK_PREVENTED_{item_type}")
                sanitized_text = re.sub(pattern, replacement, sanitized_text)
                threat_level = "HIGH"

        action = SecurityAction.SANITIZE if redacted_items else SecurityAction.ALLOW

        return SanitizationResult(
            action=action,
            original_text=text,
            sanitized_text=sanitized_text,
            flags=flags,
            threat_level=threat_level,
            redacted_items=redacted_items,
        )


# Global default instance
default_model_armor = ModelArmor()
