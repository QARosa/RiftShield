from fastapi import APIRouter, Depends

from middleware.dependencies import get_current_user, require_admin
from modules.inference.controllers import training_controller
from modules.inference.schemas.training_schema import (
    ActivateModelRequest,
    FineTuneRequest,
    StartTrainingRequest,
    TrainingLogListResponse,
    TrainingLogResponse,
)

router = APIRouter()


@router.post("/train", response_model=TrainingLogResponse)
async def start_training(
    req: StartTrainingRequest,
    user=Depends(require_admin),
) -> TrainingLogResponse:
    return await training_controller.start_training(req, str(user.id))


@router.post("/fine-tune", response_model=TrainingLogResponse)
async def fine_tune(
    req: FineTuneRequest,
    user=Depends(require_admin),
) -> TrainingLogResponse:
    return await training_controller.fine_tune_upload(req, str(user.id))


@router.get("/models", response_model=TrainingLogListResponse)
async def list_models(
    skip: int = 0,
    limit: int = 20,
    user=Depends(get_current_user),
) -> TrainingLogListResponse:
    return await training_controller.list_training_logs(skip, limit, str(user.id))


@router.get("/models/{log_id}", response_model=TrainingLogResponse)
async def get_model(
    log_id: str,
    user=Depends(get_current_user),
) -> TrainingLogResponse:
    return await training_controller.get_training_log(log_id, str(user.id))


@router.post("/models/activate")
async def activate_model(
    req: ActivateModelRequest,
    user=Depends(require_admin),
) -> dict:
    return await training_controller.activate_model(req, str(user.id))
