
from app.llm_provider import LlmRequest


class OpenRouter:
    def complete(self, message: LlmRequest) -> str:
        return "response from OpenRouter"