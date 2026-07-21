from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from beanie import Document
from pydantic import BaseModel, Field


class Threat(BaseModel):
    category: str
    description: str
    risk_level: str = Field(default="medium", pattern=r"^(low|medium|high|critical)$")


class Vulnerability(BaseModel):
    cve_id: Optional[str] = None
    title: str
    description: str
    cvss_score: Optional[float] = None
    cwe: Optional[str] = None
    affected_component: str


class Countermeasure(BaseModel):
    title: str
    description: str
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|critical)$")
    implementation_guide: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class ComponentThreatAnalysis(BaseModel):
    component_label: str
    component_class_id: int
    stride_threats: List[Threat] = Field(default_factory=list)
    vulnerabilities: List[Vulnerability] = Field(default_factory=list)
    countermeasures: List[Countermeasure] = Field(default_factory=list)


class ThreatReport(Document):
    inference_id: str
    user_id: str
    status: str = Field(default="pending", pattern=r"^(pending|processing|completed|failed)$")
    stride_summary: Dict[str, int] = Field(default_factory=dict)
    component_analyses: List[ComponentThreatAnalysis] = Field(default_factory=list)
    overall_risk_score: Optional[float] = None
    summary_text: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "threat_reports"
        use_revision = False

    class Config:
        populate_by_name = True
