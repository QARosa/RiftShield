from __future__ import annotations

from fastapi import UploadFile

from modules.inference.dataset.dataset_schema import (
    ComponentLabelResponse,
    DatasetEntryResponse,
    DatasetListResponse,
    DatasetStatsResponse,
)
from modules.inference.dataset import dataset_service


def _build_label_response(lbl):
    return ComponentLabelResponse(
        class_id=lbl.class_id,
        label=lbl.label,
        x_center=lbl.x_center,
        y_center=lbl.y_center,
        width=lbl.width,
        height=lbl.height,
    )


def _build_entry_response(entry) -> DatasetEntryResponse:
    return DatasetEntryResponse(
        id=str(entry.id),
        filename=entry.filename,
        labels=[_build_label_response(l) for l in entry.labels],
        source=entry.source,
        split=entry.split,
        augmented=entry.augmented,
        image_width=entry.image_width,
        image_height=entry.image_height,
        created_at=entry.created_at,
    )


async def upload(
    file: UploadFile,
    labels: str,
    user_id: str,
    split: str = "train",
    image_width: int = 640,
    image_height: int = 640,
) -> DatasetEntryResponse:
    import json

    parsed_labels = json.loads(labels)
    image_data = await file.read()
    entry = await dataset_service.upload_entry(
        image_data=image_data,
        filename=file.filename or "diagram.png",
        labels=parsed_labels,
        user_id=user_id,
        split=split,
        image_width=image_width,
        image_height=image_height,
    )
    return _build_entry_response(entry)


async def list_entries(
    split: str = "",
    source: str = "",
    skip: int = 0,
    limit: int = 50,
    user_id: str = "",
) -> DatasetListResponse:
    items, total = await dataset_service.list_entries(
        split=split or None,
        source=source or None,
        user_id=user_id,
        limit=limit,
        skip=skip,
    )
    return DatasetListResponse(
        total=total,
        items=[_build_entry_response(i) for i in items],
    )


async def delete_entry(
    entry_id: str,
    user_id: str = "",
) -> dict:
    deleted = await dataset_service.delete_entry(entry_id)
    return {"deleted": deleted}


async def get_stats(
    user_id: str = "",
) -> DatasetStatsResponse:
    stats = await dataset_service.get_stats()
    return DatasetStatsResponse(**stats)


async def augment_entry(
    entry_id: str,
    user_id: str = "",
) -> DatasetListResponse:
    entries = await dataset_service.augment_entry(entry_id)
    return DatasetListResponse(
        total=len(entries),
        items=[_build_entry_response(e) for e in entries],
    )
