from collections.abc import AsyncIterator
import json
import logging

from openrouter import OpenRouter
from openrouter.components import ChatFunctionToolTypedDict, ChatMessagesTypedDict

from app.config import OpenRouterConfig
from app.llm_provider import LlmMessage, LlmRequest, LlmResponse, ToolCall


logger = logging.getLogger(__name__)


class OpenRouterProvider:
    def __init__(self, config: OpenRouterConfig) -> None:
        self.config = config

    async def complete(self, request: LlmRequest) -> LlmResponse:
        messages = [self._to_openrouter_message(message) for message in request.messages]
        tools = self._build_tools(request)

        async with OpenRouter(api_key=self.config.api_key) as open_router:
            response = await open_router.chat.send_async(
                messages=messages,
                model=self.config.model,
                tools=tools,
                stream=False,
            )

        logger.debug("OpenRouter response: %s", response.model_dump_json(indent=2))

        if not response.choices:
            raise RuntimeError("OpenRouter response did not contain any choices")

        response_message = response.choices[0].message
        response_content = response_message.content
        tool_calls = response_message.tool_calls or []

        if tool_calls:
            message = response_content if isinstance(response_content, str) else None
            return LlmResponse(
                message=message,
                tool_calls=
                [
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    )
                    for tool_call in tool_calls
                ]
            )

        if not isinstance(response_content, str):
            raise RuntimeError("OpenRouter response did not contain text content")

        return LlmResponse(message=response_content)

    async def stream_complete(self, request: LlmRequest) -> AsyncIterator[str]:
        messages = [self._to_openrouter_message(message) for message in request.messages]
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

    def _build_tools(self, request: LlmRequest) -> list[ChatFunctionToolTypedDict]:
        return [
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

    def _to_openrouter_message(self, message: LlmMessage) -> ChatMessagesTypedDict:
        if message.role == "user":
            if message.content is None:
                raise RuntimeError("User message must contain content")
            return {
                "role": "user",
                "content": message.content,
            }

        if message.role == "assistant":
            assistant_message: ChatMessagesTypedDict = {
                "role": "assistant",
            }
            if message.content is not None:
                assistant_message["content"] = message.content
            elif message.tool_calls:
                assistant_message["content"] = None

            if message.tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": json.dumps(tool_call.arguments),
                        },
                    }
                    for tool_call in message.tool_calls
                ]

            return assistant_message

        if message.content is None:
            raise RuntimeError("Tool message must contain content")
        if message.tool_call_id is None:
            raise RuntimeError("Tool message must include tool_call_id")

        return {
            "role": "tool",
            "content": message.content,
            "tool_call_id": message.tool_call_id,
        }
