from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class ComponentLabelInput(BaseModel):
    class_id: int
    label: str
    x_center: float
    y_center: float
    width: float
    height: float


class ComponentLabelResponse(BaseModel):
    class_id: int
    label: str
    x_center: float
    y_center: float
    width: float
    height: float


class DatasetEntryResponse(BaseModel):
    id: str
    filename: str
    labels: List[ComponentLabelResponse]
    source: str
    split: str
    augmented: bool
    image_width: int
    image_height: int
    created_at: datetime


class DatasetListResponse(BaseModel):
    total: int
    items: List[DatasetEntryResponse]


class DatasetStatsResponse(BaseModel):
    total: int
    train_count: int
    val_count: int
    test_count: int
    manual_count: int
    augmented_count: int
    label_distribution: dict
