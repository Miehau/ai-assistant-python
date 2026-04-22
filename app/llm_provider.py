from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

from app.tools.tools import Tool


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LlmMessage:
    role: MessageRole
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None


@dataclass
class LlmRequest:
    messages: list[LlmMessage]
    tools: list[Tool]


@dataclass
class LlmResponse:
    tool_calls: list[ToolCall] = field(default_factory=list)
    message: str | None = None


class LlmProvider(Protocol):
    async def complete(self, request: LlmRequest) -> LlmResponse:
        ...

    def stream_complete(self, request: LlmRequest) -> AsyncIterator[str]:
        ...
