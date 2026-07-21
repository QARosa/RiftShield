from __future__ import annotations

from fastapi import UploadFile

from modules.inference.schemas.inference_schema import (
    AnalyzeResponse,
    BoundingBox,
    DetectedComponentResponse,
    InferenceListResponse,
)
from modules.inference.schemas.threat_schema import (
    ComponentThreatAnalysisResponse,
    CountermeasureResponse,
    ThreatReportListResponse,
    ThreatReportResponse,
    ThreatResponse,
    VulnerabilityResponse,
)
from modules.inference.services import inference_service, threat_service
from modules.inference.services.hermes_fallback import analyze_with_llm
from modules.inference.services.comparison_service import compare_architectures
from modules.inference.services.suggestion_service import suggest_architecture
from modules.hermes.models.llm_config import HermesConfig


def _build_component(c):
    return DetectedComponentResponse(
        class_id=c.class_id,
        label=c.label,
        confidence=c.confidence,
        bbox=BoundingBox(x=c.bbox[0], y=c.bbox[1], width=c.bbox[2], height=c.bbox[3]),
    )


def _build_analyze_response(inference_result) -> AnalyzeResponse:
    return AnalyzeResponse(
        id=str(inference_result.id),
        filename=inference_result.filename,
        status=inference_result.status,
        components=[_build_component(c) for c in inference_result.components],
        processing_time_ms=inference_result.processing_time_ms,
        created_at=inference_result.created_at,
    )


async def analyze(
    file: UploadFile,
    user_id: str,
) -> AnalyzeResponse:
    image_data = await file.read()
    result = await inference_service.analyze_diagram(
        image_data=image_data,
        filename=file.filename or "diagram.png",
        user_id=user_id,
    )
    return _build_analyze_response(result)


async def _get_llm_config(user_id: str) -> dict:
    cfg = {}
    try:
        from modules.auth.models.user_model import User
        user = await User.get(user_id)
        user_lang = user.language if user and user.language else "pt-BR"
        data = await HermesConfig.find_one(HermesConfig.user_id == user_id)
        if data:
            cfg = {
                "provider": data.provider, "google_api_key": data.google_api_key,
                "openai_api_key": data.openai_api_key, "deepseek_api_key": data.deepseek_api_key,
                "diag_fallback": data.diag_fallback, "language": user_lang,
            }
    except: pass
    return cfg


async def analyze_and_threat(
    file: UploadFile,
    user_id: str,
) -> dict:
    image_data = await file.read()
    filename = file.filename or "diagram.png"

    llm_config = await _get_llm_config(user_id)

    use_hermes_only = llm_config.get("diag_fallback") == "hermes"

    if use_hermes_only:
        inference = await analyze_with_llm(image_data, filename, user_id, llm_config)
        if inference is None:
            inference = await inference_service.analyze_diagram(
                image_data=image_data, filename=filename, user_id=user_id,
            )
    else:
        inference = await inference_service.analyze_diagram(
            image_data=image_data, filename=filename, user_id=user_id,
        )
        if not inference.components:
            try:
                fallback = await analyze_with_llm(image_data, filename, user_id, llm_config)
                if fallback:
                    inference = fallback
            except Exception as e:
                print(f"Fallback error: {e}")

    threat_report = await threat_service.analyze_threats(inference)
    return {
        "inference": _build_analyze_response(inference).model_dump(),
        "threat_report": _build_threat_report_response(threat_report).model_dump(),
    }


async def compare_architectures(
    file_a: UploadFile,
    file_b: UploadFile,
    user_id: str,
) -> dict:
    data_a = await file_a.read()
    data_b = await file_b.read()
    llm_config = await _get_llm_config(user_id)

    inf_a = await inference_service.analyze_diagram(data_a, file_a.filename or "arch_a.png", user_id)
    inf_b = await inference_service.analyze_diagram(data_b, file_b.filename or "arch_b.png", user_id)

    if not inf_a.components and llm_config.get("diag_fallback") != "yolo":
        try:
            fb = await analyze_with_llm(data_a, file_a.filename or "arch_a.png", user_id, llm_config)
            if fb: inf_a = fb
        except: pass
    if not inf_b.components and llm_config.get("diag_fallback") != "yolo":
        try:
            fb = await analyze_with_llm(data_b, file_b.filename or "arch_b.png", user_id, llm_config)
            if fb: inf_b = fb
        except: pass

    thr_a = await threat_service.analyze_threats(inf_a)
    thr_b = await threat_service.analyze_threats(inf_b)

    import base64
    from modules.inference.services.comparison_service import compare_architectures as _compare
    from modules.inference.models.comparison_model import ComparisonLog
    result = await _compare(inf_a, inf_b, thr_a, thr_b)
    await ComparisonLog(
        user_id=user_id,
        filename_a=file_a.filename or "arch_a.png",
        filename_b=file_b.filename or "arch_b.png",
        image_a_b64=base64.b64encode(data_a).decode("utf-8"),
        image_b_b64=base64.b64encode(data_b).decode("utf-8"),
        result=result,
    ).insert()
    return result


async def suggest_architecture_endpoint(
    file_a: UploadFile,
    file_b: UploadFile,
    user_id: str,
) -> dict:
    data_a = await file_a.read()
    data_b = await file_b.read()
    from modules.inference.models.comparison_model import ComparisonLog
    result = await suggest_architecture(data_a, data_b, file_a.filename or "arch_a.png", file_b.filename or "arch_b.png", user_id)
    if result and "error" not in result:
        log = await ComparisonLog.find_one(
            {"user_id": user_id, "filename_a": file_a.filename or "arch_a.png", "filename_b": file_b.filename or "arch_b.png"},
            sort=-ComparisonLog.created_at,
        )
        if log:
            log.suggestion = result
            await log.save()
    return result


async def list_comparisons(user_id: str) -> dict:
    from modules.inference.models.comparison_model import ComparisonLog
    items = (
        await ComparisonLog.find({"user_id": user_id})
        .sort(-ComparisonLog.created_at)
        .limit(50)
        .to_list()
    )
    return {
        "total": len(items),
        "items": [
            {
                "id": str(i.id),
                "filename_a": i.filename_a,
                "filename_b": i.filename_b,
                "image_a_b64": i.image_a_b64,
                "image_b_b64": i.image_b_b64,
                "result": i.result,
                "suggestion": i.suggestion,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in items
        ],
    }


def _build_threat_report_response(report) -> ThreatReportResponse:
    return ThreatReportResponse(
        id=str(report.id),
        inference_id=report.inference_id,
        status=report.status,
        stride_summary=report.stride_summary,
        component_analyses=[
            ComponentThreatAnalysisResponse(
                component_label=ca.component_label,
                component_class_id=ca.component_class_id,
                stride_threats=[
                    ThreatResponse(
                        category=t.category,
                        description=t.description,
                        risk_level=t.risk_level,
                    )
                    for t in ca.stride_threats
                ],
                vulnerabilities=[
                    VulnerabilityResponse(
                        cve_id=v.cve_id,
                        title=v.title,
                        description=v.description,
                        cvss_score=v.cvss_score,
                        cwe=v.cwe,
                        affected_component=v.affected_component,
                    )
                    for v in ca.vulnerabilities
                ],
                countermeasures=[
                    CountermeasureResponse(
                        title=c.title,
                        description=c.description,
                        priority=c.priority,
                        implementation_guide=c.implementation_guide,
                        references=c.references,
                    )
                    for c in ca.countermeasures
                ],
            )
            for ca in report.component_analyses
        ],
        overall_risk_score=report.overall_risk_score,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


async def list_reports(
    skip: int = 0,
    limit: int = 20,
    user_id: str = "",
) -> InferenceListResponse:
    items, total = await inference_service.list_inferences(
        user_id=user_id,
        limit=limit,
        skip=skip,
    )
    return InferenceListResponse(
        total=total,
        items=[_build_analyze_response(i) for i in items],
    )


async def get_report(
    inference_id: str,
    user_id: str = "",
) -> AnalyzeResponse:
    result = await inference_service.get_inference(inference_id)
    if not result:
        from fastapi.exceptions import HTTPException
        raise HTTPException(status_code=404, detail="Report not found")
    return _build_analyze_response(result)


async def delete_report(
    inference_id: str,
    user_id: str = "",
) -> dict:
    deleted = await inference_service.delete_inference(inference_id)
    return {"deleted": deleted}


async def list_threat_reports(
    skip: int = 0,
    limit: int = 20,
    user_id: str = "",
) -> ThreatReportListResponse:
    items, total = await threat_service.list_threat_reports(
        user_id=user_id,
        limit=limit,
        skip=skip,
    )
    return ThreatReportListResponse(
        total=total,
        items=[_build_threat_report_response(i) for i in items],
    )


async def get_threat_report(
    inference_id: str,
    user_id: str = "",
) -> ThreatReportResponse:
    report = await threat_service.get_threat_report_by_inference(inference_id)
    if not report:
        from fastapi.exceptions import HTTPException
        raise HTTPException(status_code=404, detail="Threat report not found")
    return _build_threat_report_response(report)
