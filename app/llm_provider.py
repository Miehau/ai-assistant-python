from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any, List, Literal, Protocol, Tuple, overload

from app.tools.tools import Tool


@dataclass
class LlmRequest:
    message: str
    tools: list[Tool]

@dataclass
class LlmResponse:
    tools: List[Tuple[str, Any]]
    message: str | None = None

class LlmProvider(Protocol):
      @overload
      def complete(
          self,
          request: LlmRequest,
          stream_response: Literal[False] = False,
      ) -> LlmResponse:
          ...

      @overload
      def complete(
          self,
          request: LlmRequest,
          stream_response: Literal[True],
      ) -> AsyncIterator[str]:
          ...
