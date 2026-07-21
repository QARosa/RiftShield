from __future__ import annotations

from beanie import init_beanie
from pymongo import AsyncMongoClient

from modules.auth.models.invite_model import Invite
from modules.auth.models.user_model import User
from modules.inference.dataset.dataset_model import DatasetEntry
from modules.inference.models.inference_model import InferenceResult, TrainingLog
from modules.inference.models.kb_model import KBCountermeasure, KBVulnerability
from modules.inference.models.threat_model import ThreatReport
from modules.hermes.models.chat_model import HermesMessage
from modules.hermes.models.llm_config import HermesConfig
from modules.inference.models.comparison_model import ComparisonLog
from modules.attack.models.attack_model import AttackSimulation


async def init_database(database_url: str) -> None:
    client = AsyncMongoClient(database_url, serverSelectionTimeoutMS=5000)
    db_name = database_url.rsplit("/", 1)[-1].split("?")[0] or "riftshield"
    database = client.get_database(db_name)

    await init_beanie(database=database, document_models=[
        User, Invite, DatasetEntry, InferenceResult, TrainingLog, ThreatReport,
        KBVulnerability, KBCountermeasure, HermesMessage, HermesConfig, AttackSimulation, ComparisonLog,
    ])
    print("[DB] Conectado ao MongoDB")
