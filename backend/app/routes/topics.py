from fastapi import APIRouter, HTTPException
from ..data import TOPICS

router = APIRouter()


@router.get("")
def list_topics():
    raise HTTPException(status_code=500, detail="canary fault test")
    return [
        {"slug": t["slug"], "title": t["title"], "summary": t["summary"], "icon": t["icon"]}
        for t in TOPICS
    ]


@router.get("/{slug}")
def get_topic(slug: str):
    topic = next((t for t in TOPICS if t["slug"] == slug), None)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic
