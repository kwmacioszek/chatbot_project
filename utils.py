
from __future__ import annotations
import json
import time
from typing import Awaitable, Callable
from pathlib import Path
from datetime import datetime, timezone

import logfire
from fastapi import Request, Response

_QA_LOG_PATH = Path("qa_log.jsonl")

async def log_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"
    logfire.info(
        "{method} {path} -> {status} ({duration_ms:.1f}ms)",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=duration_ms,
    )
    return response


def log_qa_pair(question: str, answer: str) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "answer": answer,
    }
    try:
        print('Logging QA pair:', entry)
        with _QA_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        logfire.exception("Failed to write qa_log entry")