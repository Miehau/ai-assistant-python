from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, Protocol

from app.tools.tools import Tool


@dataclass
class LlmRequest:
    message: str
    tools: list[Tool]


@dataclass
class LlmResponse:
    tools: list[tuple[str, Any]]
    message: str | None = None


class LlmProvider(Protocol):
    async def complete(self, request: LlmRequest) -> LlmResponse:
        ...

    def stream_complete(self, request: LlmRequest) -> AsyncIterator[str]:
        ...
