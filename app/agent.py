from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from app.llm_provider import LlmMessage, LlmProvider, LlmRequest
from app.tools.tools import Tool


@dataclass
class AgentRequest:
    message: str
    stream: bool = False
    max_iterations: int = 8


@dataclass
class Agent:
    provider: LlmProvider
    tools: list[Tool] = field(default_factory=list)
    tools_by_name: dict[str, Tool] = field(init=False)

    async def answer(self, request: AgentRequest) -> str:
        messages = [LlmMessage(role="user", content=request.message)]

        for _ in range(request.max_iterations):
            llm_response = await self.provider.complete(
                LlmRequest(messages=messages, tools=self.tools)
            )

            if llm_response.tool_calls:
                messages.append(
                    LlmMessage(
                        role="assistant",
                        content=llm_response.message,
                        tool_calls=llm_response.tool_calls,
                    )
                )

                for tool_call in llm_response.tool_calls:
                    tool = self.tools_by_name.get(tool_call.name)
                    if tool is None:
                        raise RuntimeError(f"Unknown tool requested: {tool_call.name}")

                    tool_result = await tool.run(tool_call.arguments)
                    messages.append(
                        LlmMessage(
                            role="tool",
                            content=tool_result,
                            tool_call_id=tool_call.id,
                        )
                    )
                continue

            if llm_response.message is None:
                raise RuntimeError("LLM response contained neither text nor tool calls")

            return llm_response.message

        raise RuntimeError("Agent exceeded maximum tool iterations")

    async def answer_async(self, request: AgentRequest) -> AsyncIterator[str]:
        async for chunk in self.provider.stream_complete(
            LlmRequest(
                messages=[LlmMessage(role="user", content=request.message)],
                tools=[],
            )
        ):
            yield chunk

    def __post_init__(self) -> None:
        self.tools_by_name = {
            tool.name: tool
            for tool in self.tools
        }
