from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ThreatResponse(BaseModel):
    category: str
    description: str
    risk_level: str


class VulnerabilityResponse(BaseModel):
    cve_id: Optional[str] = None
    title: str
    description: str
    cvss_score: Optional[float] = None
    cwe: Optional[str] = None
    affected_component: str


class CountermeasureResponse(BaseModel):
    title: str
    description: str
    priority: str
    implementation_guide: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class ComponentThreatAnalysisResponse(BaseModel):
    component_label: str
    component_class_id: int
    stride_threats: List[ThreatResponse] = Field(default_factory=list)
    vulnerabilities: List[VulnerabilityResponse] = Field(default_factory=list)
    countermeasures: List[CountermeasureResponse] = Field(default_factory=list)


class ThreatReportResponse(BaseModel):
    id: str
    inference_id: str
    status: str
    stride_summary: Dict[str, int]
    component_analyses: List[ComponentThreatAnalysisResponse]
    overall_risk_score: Optional[float] = None
    summary_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ThreatReportListResponse(BaseModel):
    total: int
    items: List[ThreatReportResponse]
