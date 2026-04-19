from typing import Any, Protocol


class Tool(Protocol):
    name: str
    description: str
    parameters: dict[str, Any]

    async def run(self, arguments: dict[str, Any]) -> str:
        ...