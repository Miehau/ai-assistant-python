import json

from openrouter import OpenRouter
from openrouter.components import ChatFunctionToolTypedDict, ChatMessagesTypedDict

from app.config import OpenRouterConfig
from app.llm_provider import LlmRequest, LlmResponse


class OpenRouterProvider:
    def __init__(self, config: OpenRouterConfig) -> None:
        self.config = config

    def complete(self, request: LlmRequest) -> LlmResponse:
        messages: list[ChatMessagesTypedDict] = [
            {
                "role": "user",
                "content": request.message,
            },
        ]
        tools: list[ChatFunctionToolTypedDict] = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in request.tools
        ]

        with OpenRouter(api_key=self.config.api_key) as open_router:
            response = open_router.chat.send(
                messages=messages,
                model=self.config.model,
                tools=tools,
                stream=False,
            )

        print(json.dumps(response.model_dump(), indent=2))

        if(response.choices[0].finish_reason=="tool_calls"):
            return LlmResponse(tools=
                {
                    response.choices[0].message.tool_calls[0].function.name: json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                }
            )
        
        response_content = response.choices[0].message.content

        if not isinstance(response_content, str):
            raise RuntimeError("OpenRouter response did not contain text content")

        return LlmResponse(message=response_content, tools={})
