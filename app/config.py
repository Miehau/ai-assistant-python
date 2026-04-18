from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()

@dataclass(frozen=True)
class OpenRouterConfig:
    api_key: str
    model: str


@dataclass(frozen=True)
class AppConfig:
    openrouter: OpenRouterConfig


def load_config() -> AppConfig:
    return AppConfig(
        openrouter=OpenRouterConfig(
            api_key=required_env("OPENROUTER_API_KEY"),
            model=required_env("OPENROUTER_MODEL"),
        )
    )


def required_env(name: str) -> str:
    value = os.environ.get(name)

    if value is None:
        raise RuntimeError(f"{name} is not set")

    return value
