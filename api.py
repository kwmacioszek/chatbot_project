from __future__ import annotations
from schemas import AskRequest, AskResponse, ChatRequest, ChatResponse
from agents.faq.agent import Agent
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

import storage
import utils
from agents.config import Settings
from agents.faq.agent import create_agent
from agents.handoff import  build_handoff_graph, HandoffInput
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
    app.state.handoff_graph = build_handoff_graph()
    yield


app = FastAPI(title="Air FAQ Agent API", lifespan=lifespan)
app.middleware("http")(utils.log_requests)

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest) -> AskResponse:
   agent: Agent = app.state.agent
   result = await agent.run(payload.question)
   return AskResponse(answer=result.output)


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
   session_id = payload.session_id or str(uuid.uuid4())
   history = storage.get_session(session_id)

   result = await app.state.handoff_graph.run(
       inputs=HandoffInput(payload.question, history), deps=app.state.settings
   )
   if result.messages:
       storage.save_session(session_id, result.messages)

   return ChatResponse(answer=result.output, session_id=session_id)


@app.delete("/chat/{session_id}", status_code=204)
def end_chat(session_id: str) -> None:
   if not storage.end_session(session_id):
       from fastapi import HTTPException
       raise HTTPException(status_code=404, detail="Unknown session_id")



def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()