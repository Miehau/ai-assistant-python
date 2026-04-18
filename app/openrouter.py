from app.llm_provider import LlmRequest


class OpenRouter:
    def complete(self, request: LlmRequest) -> str:
        return "response from OpenRouter"
