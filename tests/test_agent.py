from app.agent import Agent, AgentRequest
from app.llm_provider import LlmRequest, LlmResponse


class FakeProvider:
    def complete(self, request: LlmRequest) -> LlmResponse:
        return LlmResponse(message=f"fake: {request.message}", tools={})


def test_agent_delegates_to_provider() -> None:
    agent = Agent(provider=FakeProvider())

    result = agent.answer(AgentRequest(message="hello"))

    assert result == "fake: hello"
