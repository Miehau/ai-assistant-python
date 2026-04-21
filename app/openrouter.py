from collections.abc import AsyncIterator
import json

from openrouter import OpenRouter
from openrouter.components import ChatFunctionToolTypedDict, ChatMessagesTypedDict

from app.config import OpenRouterConfig
from app.llm_provider import LlmRequest, LlmResponse


class OpenRouterProvider:
    def __init__(self, config: OpenRouterConfig) -> None:
        self.config = config

    async def complete(self, request: LlmRequest) -> LlmResponse:
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

        async with OpenRouter(api_key=self.config.api_key) as open_router:
            response = await open_router.chat.send_async(
                messages=messages,
                model=self.config.model,
                tools=tools,
                stream=False,
            )

        print(json.dumps(response.model_dump(), indent=2))

        if(response.choices[0].finish_reason=="tool_calls"):
            if response.choices[0].message.tool_calls is None:
                raise RuntimeError("Tool calls returned by LLM contain no tool calls.")
            return LlmResponse(tools=
                [
                    (tool_call.function.name, json.loads(tool_call.function.arguments))
                    for tool_call in response.choices[0].message.tool_calls
                ]
            )
        
        response_content = response.choices[0].message.content

        if not isinstance(response_content, str):
            raise RuntimeError("OpenRouter response did not contain text content")

        return LlmResponse(message=response_content, tools=[])
    

    async def stream_complete(self, request: LlmRequest) -> AsyncIterator[str]:
        messages: list[ChatMessagesTypedDict] = [
            {
                "role": "user",
                "content": request.message,
            },
        ]
        tools: list[ChatFunctionToolTypedDict] = []

        async with OpenRouter(api_key=self.config.api_key) as open_router:
            stream = await open_router.chat.send_async(
                messages=messages,
                model=self.config.model,
                tools=tools,
                stream=True,
            )

            async with stream:
                async for chunk in stream:
                    if len(chunk.choices) == 0:
                        continue

                    content = chunk.choices[0].delta.content

                    if isinstance(content, str):
                        yield content
