from __future__ import annotations


from modules.inference.models.kb_model import VulnerabilityFilter
from modules.inference.schemas.kb_schema import (
    CountermeasureEntryResponse,
    CountermeasureListResponse,
    VulnerabilityEntryResponse,
    VulnerabilityListResponse,
)
from modules.inference.services import kb_service


async def list_vulnerabilities(
    component: str = "",
    cwe: str = "",
    min_cvss: float = 0,
    search: str = "",
    skip: int = 0,
    limit: int = 50,
    lang: str = "pt-BR",
    user_id: str = "",
) -> VulnerabilityListResponse:
    filt = VulnerabilityFilter(
        component=component or None,
        cwe=cwe or None,
        min_cvss=min_cvss if min_cvss > 0 else None,
        search=search or None,
    )
    items, total = await kb_service.list_vulnerabilities(
        filter_by=filt,
        skip=skip,
        limit=limit,
        lang="pt-BR",
    )
    return VulnerabilityListResponse(
        total=total,
        items=[
            VulnerabilityEntryResponse(
                id=str(v.id),
                cve_id=v.cve_id,
                title=v.title_pt or v.title,
                title_en=v.title_en or v.title,
                title_pt=v.title_pt or v.title,
                description=v.description_pt or v.description,
                description_en=v.description_en or v.description,
                description_pt=v.description_pt or v.description,
                cvss_score=v.cvss_score,
                cwe=v.cwe,
                affected_components=v.affected_components,
                tags=v.tags,
                created_at=v.created_at,
            )
            for v in items
        ],
    )


async def list_countermeasures(
    cwe: str = "",
    skip: int = 0,
    limit: int = 50,
    lang: str = "pt-BR",
    user_id: str = "",
) -> CountermeasureListResponse:
    cwe_ids = [cwe] if cwe else None
    items, total = await kb_service.list_countermeasures(
        cwe_ids=cwe_ids,
        skip=skip,
        limit=limit,
        lang="pt-BR",
    )
    return CountermeasureListResponse(
        total=total,
        items=[
            CountermeasureEntryResponse(
                id=str(c.id),
                title=c.title_pt or c.title,
                title_en=c.title_en or c.title,
                title_pt=c.title_pt or c.title,
                description=c.description_pt or c.description,
                description_en=c.description_en or c.description,
                description_pt=c.description_pt or c.description,
                priority=c.priority,
                implementation_guide=c.implementation_guide_pt or c.implementation_guide,
                implementation_guide_en=c.implementation_guide_en or c.implementation_guide,
                implementation_guide_pt=c.implementation_guide_pt or c.implementation_guide,
                references=c.references,
                vulnerability_cwe_ids=c.vulnerability_cwe_ids,
                created_at=c.created_at,
            )
            for c in items
        ],
    )
