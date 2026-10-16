import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.config import RATE_LIMIT_PER_MINUTE
from app.services import pipeline

router = APIRouter()
_requests: dict[str, deque] = defaultdict(deque)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    session_id: str = Field(default="default", max_length=64)


def _rate_limit(client: str) -> None:
    now = time.monotonic()
    hits = _requests[client]
    while hits and now - hits[0] > 60:
        hits.popleft()
    if len(hits) >= RATE_LIMIT_PER_MINUTE:
        raise HTTPException(429, "Too many questions. Please wait a minute.")
    hits.append(now)


@router.post("/chat")
def chat(body: ChatRequest, request: Request):
    _rate_limit(request.client.host if request.client else "local")
    return pipeline.ask(body.question.strip(), body.session_id)
