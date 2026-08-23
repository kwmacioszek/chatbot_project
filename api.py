from __future__ import annotations
from schemas import AskRequest, AskResponse, ChatRequest, ChatResponse
from agents.faq.agent import Agent
import uuid
from contextlib import asynccontextmanager
from typing import AsyncIterator
from pydantic_ai import BinaryContent

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Response, UploadFile

import storage
import utils
from agents.config import Settings
from agents.faq.agent import create_agent
from agents.handoff import  build_handoff_graph, HandoffInput, run_handoff
from agents.observability import configure_logfire

_AUDIO_MEDIA_TYPES = {"audio/wav", "audio/vnd.wave", "audio/mpeg"}
_AUDIO_MEDIA_TYPE_ALIASES = {"audio/vnd.wave": "audio/wav"}

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
    app.state.audio_agent = create_agent(
        settings.model_copy(update={"model_name": settings.audio_model_name})
    )
    yield


app = FastAPI(title="Air FAQ Agent API", lifespan=lifespan)
app.middleware("http")(utils.log_requests)

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, background_tasks: BackgroundTasks) -> AskResponse:
   agent: Agent = app.state.agent
   result = await agent.run(payload.question)
   background_tasks.add_task(utils.log_qa_pair, payload.question, result.output)

   return AskResponse(answer=result.output)


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
   session_id = payload.session_id or str(uuid.uuid4())
   history = storage.get_session(session_id)

   result = await run_handoff(payload.question, app.state.settings, history)
   if result.messages:
       storage.save_session(session_id, result.messages)

   return ChatResponse(answer=result.output, session_id=session_id)


@app.delete("/chat/{session_id}", status_code=204)
def end_chat(session_id: str) -> None:
   if not storage.end_session(session_id):
       from fastapi import HTTPException
       raise HTTPException(status_code=404, detail="Unknown session_id")


@app.post("/ask/audio", response_model=AskResponse)
async def ask_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)) -> AskResponse:
    if file.content_type not in _AUDIO_MEDIA_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio type '{file.content_type}'; use audio/wav or audio/mpeg (mp3).",
        )
    media_type = _AUDIO_MEDIA_TYPE_ALIASES.get(file.content_type, file.content_type)
    audio_bytes = await file.read()
    agent: Agent = app.state.audio_agent
    result = await agent.run(
        [
            "Odpowiedz na pytanie pasażera z nagrania audio.",
            BinaryContent(data=audio_bytes, media_type=media_type),
        ]
    )
    background_tasks.add_task(
        utils.log_audio_request,
        file.filename,
        file.content_type,
        len(audio_bytes),
        result.output,
    )
    return AskResponse(answer=result.output)

def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
