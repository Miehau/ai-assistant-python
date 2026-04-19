from typing import Any


class HoroscopeTool:
    name: str = "check_horoscope"
    description: str = "Checks horoscope for zodiac sign"
    parameters: dict[str, Any] = {
      "type": "object",
      "properties": {
          "sign": {
              "type": "string",
              "description": "Zodiac sign, for example Aries or Libra.",
          },
      },
      "required": ["sign"],
      "additionalProperties": False,
    }

    async def run(self, arguments: dict[str, Any]) -> str:
        sign = arguments.get("sign")
        if not isinstance(sign, str):
            raise ValueError("sign must be a string")
        match sign.lower():
            case "aries": return "All good!"
            case _: return "Bad future ahead!"