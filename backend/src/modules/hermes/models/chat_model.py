from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class HermesMessage(Document):
    user_id: str
    role: str = Field(default="user", pattern=r"^(user|agent|system)$")
    content: str = ""
    has_attachment: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "hermes_messages"
        use_revision = False

    class Config:
        populate_by_name = True
