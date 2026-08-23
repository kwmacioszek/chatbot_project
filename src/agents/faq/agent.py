"""FAQ agent definition."""

from __future__ import annotations

from pydantic_ai import Agent
from agents.model_factory import create_model
import re

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.messages import ToolCallPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from agents.faq.tools import search_faq
from agents.config import Settings

_PRICE = re.compile(r"\d+\s?(PLN|zł|EUR|€)", re.IGNORECASE)

INSTRUCTIONS = (
    "Jesteś asystentem obsługi klienta linii lotniczej Example Air. "
    "Odpowiadasz po polsku, krótko i uprzejmie.\n"
    "Zasady:\n"
    "- Zanim odpowiesz na pytanie o zasady przewozu, opłaty czy procedury, "
    "zawsze sprawdź bazę FAQ narzędziem search_faq.\n"
    "- Baza FAQ jest po angielsku — szukaj angielskich słów kluczowych, "
    "a pasażerowi odpowiadaj po polsku.\n"
    "- Odpowiadaj wyłącznie na podstawie informacji z FAQ. Nie wymyślaj "
    "cen, limitów ani procedur, których tam nie ma.\n"
    "- Jeśli FAQ nie zawiera odpowiedzi, powiedz to wprost i skieruj "
    "pasażera na infolinię (temat 'helpline contact').\n"
    "- Nie masz dostępu do rezerwacji pasażerów — sprawy indywidualne "
    "(np. status konkretnego lotu) kieruj na infolinię."
)

_PRICE = re.compile(r"\d+\s?(PLN|zł|EUR|€)", re.IGNORECASE)


def create_agent(settings: Settings) -> Agent:
    agent = Agent(create_model(settings), instructions=INSTRUCTIONS)
    agent.tool_plain(search_faq)

    @agent.output_validator
    def guard_price_claims(ctx: RunContext[None], output: str) -> str:
        """Blocks a price/amount in the answer unless search_faq was called first."""
        if _PRICE.search(output):
            called_faq = any(
                isinstance(part, ToolCallPart) and part.tool_name == "search_faq"
                for message in ctx.messages
                for part in message.parts
            )
            if not called_faq:
                raise ModelRetry(
                    "Podałeś kwotę, ale nie wywołałeś search_faq — "
                    "sprawdź FAQ, zanim podasz cenę."
                )
        return output
    return agent
