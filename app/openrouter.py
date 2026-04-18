from openrouter import OpenRouter

from app.config import OpenRouterConfig
from app.llm_provider import LlmRequest


class OpenRouterProvider:
    def __init__(self, config: OpenRouterConfig) -> None:
        self.config = config

    def complete(self, request: LlmRequest) -> str:
        with OpenRouter(api_key=self.config.api_key) as open_router:
            response = open_router.chat.send(
                messages=[
                    {
                         "role": "user",
                         "content": request.message
                    }
                ],
                model=self.config.model,
                stream=False
            )
        response_content = response.choices[0].message.content
        if not isinstance(response_content, str):
            raise RuntimeError("OpenRouter response did not contain text content")
        return response_content
