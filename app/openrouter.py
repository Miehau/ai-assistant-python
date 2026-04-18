from dataclasses import dataclass

from app.config import OpenRouterConfig
from app.llm_provider import LlmRequest


@dataclass
class OpenRouter:
    config: OpenRouterConfig
    
    def complete(self, request: LlmRequest) -> str:
        return "response from OpenRouter"
