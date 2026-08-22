"""Command-line interface for the FAQ agent with triage hand-off.

Usage:
    faq-agent-handoff                  # interactive mode (conversation)
    faq-agent-handoff "your question"  # single question
"""

from __future__ import annotations

import sys

from pydantic_ai.messages import ModelMessage

from agents.config import Settings
from agents.handoff import ask
from agents.observability import configure_logfire


def main() -> None:
    settings = Settings()
    if not settings.openai_api_key:
        sys.exit(
            "Missing API key. Set OPENAI_API_KEY in the .env file in the working directory\n"
            "(or set the OPENAI_API_KEY environment variable)."
        )

    configure_logfire(settings.logfire_token)

    if len(sys.argv) > 1:
        # One-shot mode: question passed as an argument.
        result = ask(" ".join(sys.argv[1:]), settings)
        print(result.output)
        return

    print("Example Air airline FAQ agent with hand-off (type 'exit' to quit)")
    history: list[ModelMessage] = []
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        result = ask(question, settings, message_history=history)
        history = result.messages or history  # conversation memory between turns
        print(f"\nAgent: {result.output}")


if __name__ == "__main__":
    main()