from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.agent import Agent, AgentRequest
from app.llm_provider import LlmRequest, LlmResponse


class FakeProvider:
    def complete(self, request: LlmRequest) -> LlmResponse:
        return LlmResponse(message=f"fake: {request.message}", tools={})
    
    async def complete_stream(self, request: LlmRequest) -> AsyncIterator[str]:
        yield "Hel"
        yield "lo"


class FakeToolProvider:
    def complete(self, request: LlmRequest) -> LlmResponse:
        return LlmResponse(
            message=None,
            tools={
                "fake_tool": {
                    "name": "Michal",
                },
            },
        )

    def complete_stream(self, request: LlmRequest) -> AsyncIterator[str]:
        raise AssertionError("complete_stream should not be called")


class FakeTool:
    name = "fake_tool"
    description = "Fake tool for tests"
    parameters: dict[str, Any] = {}

    async def run(self, arguments: dict[str, Any]) -> str:
        assert arguments == {"name": "Michal"}
        return "Hello Michal"


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


@pytest.mark.asyncio
async def test_agent_runs_tool_calls() -> None:
    agent = Agent(provider=FakeToolProvider(), tools=[FakeTool()])

    result = await agent.answer(AgentRequest(message="hello"))

    assert result == "fake_tool: Hello Michal"
