"""Agent configuration — from a .env file or environment variables."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from a .env file in the working directory.

    Environment variables take precedence over the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    provider: Literal["openai", "gemini", "lmstudio"] = "openai"
    openai_api_key: str = ""  # OPENAI_API_KEY variable
    gemini_api_key: str = ""  # GEMINI_API_KEY variable
    lmstudio_base_url: str = "http://localhost:1234/v1"  # LMSTUDIO_BASE_URL variable
    lmstudio_api_key: str = "lm-studio"  # LMSTUDIO_API_KEY variable
    model_name: str = "gpt-4o-mini"  # MODEL_NAME variable
    logfire_token: str = ""  # LOGFIRE_TOKEN variable (optional)
