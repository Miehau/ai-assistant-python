from dataclasses import dataclass
from typing import Protocol


@dataclass
class LlmRequest:
    message: str


class LlmProvider(Protocol):
    def complete(self, request: LlmRequest) -> str:
        ...
