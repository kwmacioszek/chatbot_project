"""Interactive command-line chat with the FAQ agent."""

from __future__ import annotations

from agents.config import Settings
from observability import configure_logfire
from agents.faq.agent import create_agent


def main() -> None:
    """Starts an interactive chat loop in the terminal (Ctrl+C or 'exit' to quit)."""
    settings = Settings()
    agent = create_agent(settings)

    print("Example Air FAQ agent — wpisz pytanie (Ctrl+C lub 'exit' aby zakończyć)\n")
    configure_logfire(settings.logfire_token)

    message_history = None
    while True:
        try:
            user_input = input("Ty: ").strip()
        except (KeyboardInterrupt, EOFError):
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break
        result = agent.run_sync(user_input, message_history=message_history)
        print(f"Agent: {result.output}\n")
        message_history = result.all_messages()


if __name__ == "__main__":
    main()
