from collections.abc import AsyncIterator

import pytest

from app.agent import Agent, AgentRequest
from app.llm_provider import LlmRequest, LlmResponse


class FakeProvider:
    def complete(self, request: LlmRequest) -> LlmResponse:
        return LlmResponse(message=f"fake: {request.message}", tools={})
    
    async def complete_stream(self, request: LlmRequest) -> AsyncIterator[str]:
        yield "Hel"
        yield "lo"


@pytest.mark.asyncio
async def test_agent_delegates_to_provider() -> None:
    agent = Agent(provider=FakeProvider())

    result = await agent.answer(AgentRequest(message="hello"))

    assert result == "fake: hello"


@pytest.mark.asyncio
async def test_agent_delegates_stream_to_provider() -> None:
    agent = Agent(provider=FakeProvider())

    chunks: list[str] = []
    async for chunk in agent.answer_async(AgentRequest(message="Hello")):
        chunks.append(chunk)

    assert chunks == ["Hel", "lo"]