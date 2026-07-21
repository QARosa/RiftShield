from __future__ import annotations

from beanie import Document
from pydantic import Field


class HermesConfig(Document):
    user_id: str
    enabled: bool = True
    provider: str = Field(default="google", pattern=r"^(google|openai|deepseek)$")
    google_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    google_model: str = "gemini-2.5-flash-lite"
    openai_model: str = "gpt-4o-mini"
    deepseek_model: str = "deepseek-chat"
    diag_fallback: str = "yolo"
    fallback_enabled: bool = True

    class Settings:
        name = "hermes_configs"
        use_revision = False

    class Config:
        populate_by_name = True
