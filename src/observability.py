"""Logfire instrumentation for the FAQ agent.

Logfire (https://logfire.pydantic.dev/) is Pydantic's observability
platform; it understands Pydantic AI natively and shows each agent run as
a trace with model requests, tool calls, and token usage.
"""

from __future__ import annotations

import logfire


def configure_logfire(token: str = "") -> None:
    """Configures Logfire and instruments Pydantic AI.

    Sends traces to Logfire when a token is given (see
    https://logfire.pydantic.dev/ -> project -> write token). Without a
    token, Logfire just prints a local summary to the console instead of
    failing, so the agent works the same with or without it configured.

    The token is passed explicitly (from Settings/.env) rather than read
    from the environment, since python-dotenv-style loading via
    pydantic-settings doesn't export LOGFIRE_TOKEN to os.environ.
    """
    logfire.configure(token=token or None, send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()