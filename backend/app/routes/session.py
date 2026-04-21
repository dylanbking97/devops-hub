import uuid
import json
from fastapi import APIRouter, Request, Response, HTTPException
from ..config import get_redis

router = APIRouter()

SESSION_TTL = 86400
COOKIE_NAME = "session_id"


def _get_session_id(request: Request) -> str | None:
    return request.cookies.get(COOKIE_NAME)


def _load(redis, session_id: str) -> dict:
    raw = redis.get(f"session:{session_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="Session not found")
    return json.loads(raw)


def _save(redis, session_id: str, data: dict) -> dict:
    redis.setex(f"session:{session_id}", SESSION_TTL, json.dumps(data))
    return {"session_id": session_id, **data}


@router.post("")
def create_session(response: Response):
    redis = get_redis()
    session_id = str(uuid.uuid4())
    data = _save(redis, session_id, {"visited": [], "completed": []})
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_id,
        httponly=True,       # not readable by JS — protects against XSS
        max_age=SESSION_TTL,
        samesite="lax",      # sent on same-site requests and top-level navigations
    )
    return data


@router.get("")
def get_session(request: Request):
    session_id = _get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=404, detail="No session cookie")
    return _load(get_redis(), session_id) | {"session_id": session_id}


@router.post("/visit/{topic_slug}")
def visit_topic(topic_slug: str, request: Request):
    session_id = _get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=404, detail="No session cookie")
    redis = get_redis()
    data = _load(redis, session_id)
    if topic_slug not in data["visited"]:
        data["visited"].append(topic_slug)
    return _save(redis, session_id, data)


@router.post("/complete/{topic_slug}")
def complete_topic(topic_slug: str, request: Request):
    session_id = _get_session_id(request)
    if not session_id:
        raise HTTPException(status_code=404, detail="No session cookie")
    redis = get_redis()
    data = _load(redis, session_id)
    if topic_slug not in data["visited"]:
        data["visited"].append(topic_slug)
    if topic_slug not in data["completed"]:
        data["completed"].append(topic_slug)
    return _save(redis, session_id, data)
