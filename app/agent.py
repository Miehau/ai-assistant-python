from dataclasses import dataclass
import json

from app.llm_provider import LlmProvider, LlmRequest
from app.tools.tools import Tool


@dataclass
class AgentRequest:
    message: str


@dataclass
class Agent:
    provider: LlmProvider
    tools: list[Tool]

    def answer(self, request: AgentRequest) -> str:
        tool_by_name = {
            tool.name : tool
            for tool in self.tools
        }
        llm_response = self.provider.complete(LlmRequest(message=request.message, tools=self.tools))
        if llm_response.message is not None:
            return llm_response.message
        for tool_name, arguments in llm_response.tools.items():
            tool = tool_by_name[tool_name]
            return tool.run(arguments)
        raise RuntimeError("LLM returned neither message nor tool call")
