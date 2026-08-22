from __future__ import annotations
from schemas import AskRequest, AskResponse
from agents.faq.agent import Agent  
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from agents.config import Settings
from agents.faq.agent import create_agent
from agents.handoff import handoff_graph
from agents.observability import configure_logfire


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "Missing API key. Set OPENAI_API_KEY in the .env file in the "
            "working directory (or set the OPENAI_API_KEY environment variable)."
        )
    configure_logfire(settings.logfire_token)
    app.state.settings = settings
    app.state.agent = create_agent(settings)
    app.state.handoff_graph = handoff_graph
    yield


app = FastAPI(title="Air FAQ Agent API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
   agent: Agent = app.state.agent
   result = await agent.run(payload.question)
   return AskResponse(answer=result.output)




def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()