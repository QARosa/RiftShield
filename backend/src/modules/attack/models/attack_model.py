from __future__ import annotations

from datetime import datetime
from typing import List

from beanie import Document
from pydantic import Field


class AttackSimulation(Document):
    user_id: str
    attack_type: str
    target_component: str
    severity: str = Field(default="medium")
    description: str = ""
    technical_details: str = ""
    countermeasures: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "attack_simulations"
        use_revision = False

    class Config:
        populate_by_name = True
