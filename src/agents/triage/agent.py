"""Triage agent definition."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel
from pydantic_ai import Agent

from agents.config import Settings
from agents.model_factory import create_model

TRIAGE_INSTRUCTIONS = (
    "Jesteś agentem triażu obsługi klienta linii lotniczej Example Air.\n"
    "Zdecyduj, dokąd skierować pytanie pasażera:\n"
    "- target='faq' — pytania ogólne o zasady, opłaty i procedury "
    "(bagaż, odprawa, zmiany rezerwacji, zwroty, zwierzęta, dzieci itp.).\n"
    "- target='human' — sprawy wymagające dostępu do danych konkretnego "
    "pasażera lub rezerwacji (np. status konkretnego lotu lub szczegóły "
    "konkretnej rezerwacji).\n"
    "- target='complaint' — reklamacje, odszkodowania i skargi dotyczące "
    "zakupionego biletu lub odbytego lotu."
)


class Triage(BaseModel):
    """Routing decision made by the triage agent."""

    target: Literal["faq", "human", "complaint"]
    reason: str


def create_triage_agent(settings: Settings) -> Agent[None, Triage]:
    """Builds the triage agent that decides where to hand off the question."""
    return Agent(
        create_model(settings),
        instructions=TRIAGE_INSTRUCTIONS,
        output_type=Triage,
    )
