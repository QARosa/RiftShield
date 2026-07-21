from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class VulnerabilityEntryResponse(BaseModel):
    id: str
    cve_id: Optional[str] = None
    title: str
    title_en: Optional[str] = None
    title_pt: Optional[str] = None
    description: str
    description_en: Optional[str] = None
    description_pt: Optional[str] = None
    cvss_score: Optional[float] = None
    cwe: Optional[str] = None
    affected_components: List[str]
    tags: List[str]
    created_at: datetime


class CountermeasureEntryResponse(BaseModel):
    id: str
    title: str
    title_en: Optional[str] = None
    title_pt: Optional[str] = None
    description: str
    description_en: Optional[str] = None
    description_pt: Optional[str] = None
    implementation_guide: Optional[str] = None
    implementation_guide_en: Optional[str] = None
    implementation_guide_pt: Optional[str] = None
    priority: str
    references: List[str]
    vulnerability_cwe_ids: List[str]
    created_at: datetime


class VulnerabilityListResponse(BaseModel):
    total: int
    items: List[VulnerabilityEntryResponse]


class CountermeasureListResponse(BaseModel):
    total: int
    items: List[CountermeasureEntryResponse]
