from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile

from middleware.dependencies import get_current_user
from modules.inference.dataset.dataset_controller import (
    augment_entry,
    delete_entry,
    get_stats,
    list_entries,
    upload,
)
from modules.inference.dataset.dataset_schema import (
    DatasetEntryResponse,
    DatasetListResponse,
    DatasetStatsResponse,
)

router = APIRouter()


@router.post("/upload", response_model=DatasetEntryResponse)
async def upload_entry(
    file: UploadFile = File(...),
    labels: str = Form(...),
    split: str = Form("train"),
    image_width: int = Form(640),
    image_height: int = Form(640),
    user=Depends(get_current_user),
) -> DatasetEntryResponse:
    return await upload(file, labels, str(user.id), split, image_width, image_height)


@router.get("/entries", response_model=DatasetListResponse)
async def list_dataset_entries(
    split: str = "",
    source: str = "",
    skip: int = 0,
    limit: int = 50,
    user=Depends(get_current_user),
) -> DatasetListResponse:
    return await list_entries(split, source, skip, limit, str(user.id))


@router.delete("/entries/{entry_id}")
async def delete_dataset_entry(
    entry_id: str,
    user=Depends(get_current_user),
) -> dict:
    return await delete_entry(entry_id, str(user.id))


@router.post("/entries/{entry_id}/augment", response_model=DatasetListResponse)
async def augment_dataset_entry(
    entry_id: str,
    user=Depends(get_current_user),
) -> DatasetListResponse:
    return await augment_entry(entry_id, str(user.id))


@router.get("/stats", response_model=DatasetStatsResponse)
async def dataset_stats(
    user=Depends(get_current_user),
) -> DatasetStatsResponse:
    return await get_stats(str(user.id))
