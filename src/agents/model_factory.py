# src/agents/model_factory.py
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider

from agents.config import Settings


def create_openai_model(settings: Settings):
    return OpenAIChatModel(
        settings.model_name,
        provider=OpenAIProvider(api_key=settings.openai_api_key),
    )


def create_gemini_model(settings: Settings):
    return GoogleModel(
        settings.model_name,
        provider=GoogleProvider(api_key=settings.gemini_api_key),
    )


def create_lmstudio_model(settings: Settings):
    return OpenAIChatModel(
        settings.model_name,
        provider=OpenAIProvider(
            base_url=settings.lmstudio_base_url,
            api_key=settings.lmstudio_api_key,
        ),
    )


MODEL_FACTORIES = {
    "openai": create_openai_model,
    "gemini": create_gemini_model,
    "lmstudio": create_lmstudio_model,
}


def create_model(settings: Settings):
    try:
        return MODEL_FACTORIES[settings.provider](settings)
    except KeyError as exc:
        raise ValueError(f"Nieobsługiwany provider: {settings.provider}") from exc