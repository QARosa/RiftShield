from __future__ import annotations


from modules.inference.models.inference_model import TrainingLog
from modules.inference.schemas.training_schema import (
    ActivateModelRequest,
    StartTrainingRequest,
    TrainingLogListResponse,
    TrainingLogResponse,
)
from modules.inference.services import training_service
from modules.inference.schemas.training_schema import FineTuneRequest
def _build_log_response(log: TrainingLog) -> TrainingLogResponse:
    return TrainingLogResponse(
        id=str(log.id),
        model_type=log.model_type,
        dataset_version=log.dataset_version,
        hyperparameters=log.hyperparameters,
        metrics=log.metrics,
        model_path=log.model_path,
        status=log.status,
        started_at=log.started_at,
        completed_at=log.completed_at,
        created_at=log.created_at,
    )


async def start_training(
    req: StartTrainingRequest,
    user_id: str,
) -> TrainingLogResponse:
    log = await training_service.fine_tune(
        user_id=user_id,
        image_paths=[],
        labels=[],
        epochs=req.epochs,
    )
    return _build_log_response(log)


async def fine_tune_upload(
    req: FineTuneRequest,
    user_id: str = "",
) -> TrainingLogResponse:
    log = await training_service.fine_tune(
        user_id=user_id,
        epochs=req.epochs,
    )
    return _build_log_response(log)


async def list_training_logs(
    skip: int = 0,
    limit: int = 20,
    user_id: str = "",
) -> TrainingLogListResponse:
    items, total = await training_service.list_training_logs(
        limit=limit, skip=skip
    )
    return TrainingLogListResponse(
        total=total,
        items=[_build_log_response(i).model_dump() for i in items],
    )


async def get_training_log(
    log_id: str,
    user_id: str = "",
) -> TrainingLogResponse:
    log = await training_service.get_training_log(log_id)
    if not log:
        from fastapi.exceptions import HTTPException
        raise HTTPException(status_code=404, detail="Training log not found")
    return _build_log_response(log)


async def activate_model(
    req: ActivateModelRequest,
    user_id: str,
) -> dict:
    ok = await training_service.activate_model(req.model_path)
    return {"activated": ok}
