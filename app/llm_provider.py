from dataclasses import dataclass
from typing import Any, Protocol

from app.tools.tools import Tool


@dataclass
class LlmRequest:
    message: str
    tools: list[Tool]

@dataclass
class LlmResponse:
    tools: dict[str, Any]
    message: str | None = None

class LlmProvider(Protocol):
    def complete(self, request: LlmRequest) -> LlmResponse:
        ...
