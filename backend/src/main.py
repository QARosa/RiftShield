from __future__ import annotations

from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from config.database import init_database
from config.settings import get_settings
from middleware.error_handler import app_error_handler, validation_error_handler
from middleware.refresh_middleware import RefreshTokenMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from modules.auth import auth_router
from modules.hermes import hermes_router
from modules.attack import attack_router
from modules.export import export_router
from modules.dashboard.routes.dashboard_routes import router as dashboard_router
from modules.inference.dataset.dataset_routes import router as dataset_router
from modules.inference.routes.inference_routes import router as inference_router
from modules.inference.routes.kb_routes import router as kb_router
from modules.inference.routes.training_routes import router as training_router
from modules.users import user_router
from shared.utils.errors import AppError

load_dotenv()
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_database(settings.database_url)
    from modules.auth.models.invite_model import Invite
    existing = await Invite.find_one({"used": False})
    if not existing:
        import secrets
        code = secrets.token_hex(16)
        await Invite(code=code, role="ADMIN").insert()
        print(f"🔑 Invite code created: {code}")
    from modules.inference.services.kb_service import seed_knowledge_base
    seeded = await seed_knowledge_base()
    if seeded:
        print(f"\U0001f4da Knowledge base seeded: {seeded} entries")

    from modules.inference.models.inference_model import TrainingLog
    from pathlib import Path
    from datetime import datetime
    best_pt = Path(__file__).resolve().parent / "modules" / "inference" / "train_results" / "best.pt"
    existing_log = await TrainingLog.find_one({"is_base_model": True})
    if best_pt.exists() and not existing_log:
        import yaml
        try:
            args_yaml = Path(__file__).resolve().parent.parent / "models" / "architecture_yolo" / "args.yaml"
            if args_yaml.exists():
                with open(args_yaml) as f:
                    meta = yaml.safe_load(f)
                    meta.get("epochs", 9)
            await TrainingLog(
                model_type="yolov8n",
                model_name="Pré-treinado architecture_merged (9 épocas)",
                dataset_version="architecture_merged_roboflow",
                hyperparameters={"epochs": 9, "imgsz": 640, "batch": 16, "fine_tune": False},
                metrics={"mAP50": 0.579, "mAP50_95": 0.411, "precision": 0.731, "recall": 0.554},
                model_path=str(best_pt),
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                train_images_count=4740,
                val_images_count=279,
                classes_count=34,
                trained_filenames=[],
                is_base_model=True,
            ).insert()
            print(f"✅ Modelo pré-treinado registrado: {best_pt}")
        except Exception as e:
            print(f"⚠️ Erro ao registrar modelo base: {e}")
    yield


app = FastAPI(title="RiftShield API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RefreshTokenMiddleware)
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/auth")
app.include_router(user_router, prefix="/api/users")
app.include_router(dashboard_router, prefix="/api/dashboard")
app.include_router(inference_router, prefix="/api/inference")
app.include_router(dataset_router, prefix="/api/dataset")
app.include_router(kb_router, prefix="/api/kb")
app.include_router(training_router, prefix="/api/training")
app.include_router(hermes_router, prefix="/api/hermes")
app.include_router(attack_router, prefix="/api/attack")
app.include_router(export_router, prefix="/api/export")
