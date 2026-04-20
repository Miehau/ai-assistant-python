from functools import wraps
import logging
from typing import Any, Protocol

class Tool(Protocol):
    name: str
    description: str
    parameters: dict[str, Any]

    async def run(self, arguments: dict[str, Any]) -> str:
        ...

# FIXME: Try this logger with proper inheritance and having a default method. 
# This way I won't have to wrap each tool
def log_tool_call(func):
    @wraps(func)
    async def wrapper(self: Any, arguments: dict[str, Any]):
        tool_logger = logging.getLogger(self.__class__.__module__)
        tool_name=getattr(self, "name", self.__class__.__name__)
        tool_logger.info("Calling tool %s with arguments=%r", tool_name, arguments)
        result=await func(self, arguments)
        tool_logger.info("Tool %s returned result=%r", tool_name, result)
        return result
    return wrapper