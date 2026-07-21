from __future__ import annotations

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import Field


class ComparisonLog(Document):
    user_id: str
    comparison_type: str = "full"
    baseline_model: Optional[str] = None
    candidate_model: Optional[str] = None
    summary: Optional[str] = None
    metrics: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "comparison_logs"
        use_revision = False

    class Config:
        populate_by_name = True
