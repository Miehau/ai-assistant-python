from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from app.llm_provider import LlmProvider, LlmRequest, LlmResponse
from app.tools.tools import Tool


@dataclass
class AgentRequest:
    message: str
    stream: bool = False


@dataclass
class Agent:
    provider: LlmProvider
    tools: list[Tool] = field(default_factory=list)
    tools_by_name: dict[str, Tool] = field(init=False)

    async def answer(self, request: AgentRequest) -> str:
        llm_response = self.provider.complete(LlmRequest(message=request.message, tools=self.tools))
        if llm_response.message is not None:
            return llm_response.message
        
        tool_outcomes = {
            tool_name: await self.tools_by_name[tool_name].run(arguments)
            for tool_name, arguments in llm_response.tools.items()
        }
        return "\n".join(
            f"{tool_name}: {tool_outcome}"
            for tool_name, tool_outcome in tool_outcomes.items()
        )


    
    async def answer_async(self, request: AgentRequest) -> AsyncIterator[str]:
        async for chunk in self.provider.complete(
            LlmRequest(message=request.message, tools=[]),
            stream_response=True,
        ):
            yield chunk

    
    def __post_init__(self) -> None:
        self.tools_by_name = {
            tool.name: tool
            for tool in self.tools
        }
