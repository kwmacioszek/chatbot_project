"""Triage agent definition."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from agents.config import Settings

TRIAGE_INSTRUCTIONS = (
    "Jesteś agentem triażu obsługi klienta linii lotniczej Example Air.\n"
    "Zdecyduj, dokąd skierować pytanie pasażera:\n"
    "- target='faq' — pytania ogólne o zasady, opłaty i procedury "
    "(bagaż, odprawa, zmiany rezerwacji, zwroty, zwierzęta, dzieci itp.).\n"
    "- target='human' — sprawy wymagające dostępu do danych konkretnego "
    "pasażera lub rezerwacji (np. status konkretnego lotu, reklamacja "
    "dotycząca już zakupionego biletu)."
)


class Triage(BaseModel):
    """Routing decision made by the triage agent."""

    target: Literal["faq", "human"]
    reason: str


def create_triage_agent(settings: Settings) -> Agent[None, Triage]:
    """Builds the triage agent that decides where to hand off the question."""
    return Agent(
        OpenAIChatModel(
            settings.model_name,
            provider=OpenAIProvider(api_key=settings.openai_api_key),
        ),
        instructions=TRIAGE_INSTRUCTIONS,
        output_type=Triage,
    )