from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.agent import Agent, AgentRequest
from app.llm_provider import LlmMessage, LlmRequest, LlmResponse, MessageRole, ToolCall


class FakeProvider:
    async def complete(self, request: LlmRequest) -> LlmResponse:
        assert request.messages == [LlmMessage(role=MessageRole.USER, content="hello")]
        return LlmResponse(message="fake: hello")
    
    async def stream_complete(self, request: LlmRequest) -> AsyncIterator[str]:
        assert request.messages == [LlmMessage(role=MessageRole.USER, content="Hello")]
        yield "Hel"
        yield "lo"


class FakeToolProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, request: LlmRequest) -> LlmResponse:
        self.calls += 1

        if self.calls == 1:
            assert request.messages == [LlmMessage(role=MessageRole.USER, content="hello")]
            return LlmResponse(
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="fake_tool",
                        arguments={"name": "Michal"},
                    )
                ]
            )

        assert request.messages == [
            LlmMessage(role=MessageRole.USER, content="hello"),
            LlmMessage(
                role=MessageRole.ASSISTANT,
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="fake_tool",
                        arguments={"name": "Michal"},
                    )
                ],
            ),
            LlmMessage(
                role=MessageRole.TOOL,
                content="Hello Michal",
                tool_call_id="call-1",
            ),
        ]
        return LlmResponse(message="Done after tool")

    async def stream_complete(self, request: LlmRequest) -> AsyncIterator[str]:
        raise AssertionError("streaming should not be called")


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
    provider = FakeToolProvider()
    agent = Agent(provider=provider, tools=[FakeTool()])

    result = await agent.answer(AgentRequest(message="hello"))

    assert result == "Done after tool"
    assert provider.calls == 2
