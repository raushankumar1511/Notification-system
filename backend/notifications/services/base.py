"""Shared types for provider clients.

Every provider returns a :class:`SendResult`. Providers never raise for expected
failures (missing keys, provider errors) — they return a result the send pipeline turns
into a NotificationLog row. This keeps a single failing channel from breaking a trigger.
"""

from dataclasses import dataclass, field


@dataclass
class SendResult:
    status: str  # "sent" | "failed" | "skipped"
    provider_message_id: str = ""
    error: str = ""
    payload: dict = field(default_factory=dict)

    @classmethod
    def sent(cls, message_id: str = "", payload: dict | None = None) -> "SendResult":
        return cls(status="sent", provider_message_id=message_id, payload=payload or {})

    @classmethod
    def failed(cls, error: str, payload: dict | None = None) -> "SendResult":
        return cls(status="failed", error=error, payload=payload or {})

    @classmethod
    def skipped(cls, error: str, payload: dict | None = None) -> "SendResult":
        return cls(status="skipped", error=error, payload=payload or {})
