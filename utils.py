
from __future__ import annotations

import time
from typing import Awaitable, Callable

import logfire
from fastapi import Request, Response


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