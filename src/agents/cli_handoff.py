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
    api_keys = {
        "openai": ("OPENAI_API_KEY", settings.openai_api_key),
        "gemini": ("GEMINI_API_KEY", settings.gemini_api_key),
        "lmstudio": ("LMSTUDIO_API_KEY", settings.lmstudio_api_key),
    }
    key_name, api_key = api_keys[settings.provider]
    if not api_key:
        sys.exit(f"Missing API key. Set {key_name} in the .env file or environment.")

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
