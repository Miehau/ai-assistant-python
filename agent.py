

from dataclasses import dataclass

from llm_provider import LlmProvider, LlmRequest


@dataclass
class AgentRequest:
    message: str

@dataclass
class Agent:
    provider: LlmProvider

    def answer(self, request: AgentRequest) -> str:
        return self.provider.complete(LlmRequest(message=request.message))