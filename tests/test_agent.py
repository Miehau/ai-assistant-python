from app.agent import Agent, AgentRequest
from app.llm_provider import LlmRequest


class FakeProvider:
    def complete(self, request: LlmRequest) -> str:
        return f"fake: {request.message}"


def test_agent_delegates_to_provider() -> None:
    agent = Agent(provider=FakeProvider())

    result = agent.answer(AgentRequest(message="hello"))

    assert result == "fake: hello"
