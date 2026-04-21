from pydantic import BaseModel
from typing import List


class TopicSummary(BaseModel):
    slug: str
    title: str
    summary: str
    icon: str


class Topic(TopicSummary):
    content: str  # markdown


class SessionData(BaseModel):
    session_id: str
    visited: List[str] = []
    completed: List[str] = []
