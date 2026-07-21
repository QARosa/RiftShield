from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class DetectedComponentResponse(BaseModel):
    class_id: int
    label: str
    confidence: float
    bbox: BoundingBox


class AnalyzeResponse(BaseModel):
    id: str
    filename: str
    status: str
    components: List[DetectedComponentResponse]
    processing_time_ms: Optional[float] = None
    created_at: datetime


class InferenceListResponse(BaseModel):
    total: int
    items: List[AnalyzeResponse]


class TrainingMetrics(BaseModel):
    mAP50: Optional[float] = None
    mAP50_95: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    epochs_completed: Optional[int] = None


class TrainingLogResponse(BaseModel):
    id: str
    model_type: str
    dataset_version: str
    hyperparameters: dict
    metrics: TrainingMetrics
    model_path: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
