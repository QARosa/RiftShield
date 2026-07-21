
from fastapi import APIRouter, Depends, File, UploadFile

from middleware.dependencies import get_current_user
from modules.inference.controllers import inference_controller
from modules.inference.schemas.inference_schema import AnalyzeResponse, InferenceListResponse
from modules.inference.schemas.threat_schema import ThreatReportListResponse, ThreatReportResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_diagram(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
) -> AnalyzeResponse:
    return await inference_controller.analyze(file, str(user.id))


@router.post("/analyze-threat", response_model=dict)
async def analyze_diagram_with_threats(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
) -> dict:
    return await inference_controller.analyze_and_threat(file, str(user.id))


@router.post("/compare")
async def compare_architectures(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    user=Depends(get_current_user),
) -> dict:
    return await inference_controller.compare_architectures(file_a, file_b, str(user.id))


@router.post("/suggest")
async def suggest_architecture(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    user=Depends(get_current_user),
) -> dict:
    return await inference_controller.suggest_architecture_endpoint(file_a, file_b, str(user.id))


@router.get("/comparisons")
async def list_comparisons(
    user=Depends(get_current_user),
) -> dict:
    return await inference_controller.list_comparisons(str(user.id))


@router.get("/reports", response_model=InferenceListResponse)
async def list_reports(
    skip: int = 0,
    limit: int = 20,
    user=Depends(get_current_user),
) -> InferenceListResponse:
    return await inference_controller.list_reports(skip, limit, str(user.id))


@router.get("/reports/{inference_id}", response_model=AnalyzeResponse)
async def get_report(
    inference_id: str,
    user=Depends(get_current_user),
) -> AnalyzeResponse:
    return await inference_controller.get_report(inference_id, str(user.id))


@router.delete("/reports/{inference_id}")
async def delete_report(
    inference_id: str,
    user=Depends(get_current_user),
) -> dict:
    return await inference_controller.delete_report(inference_id, str(user.id))


@router.get("/threats", response_model=ThreatReportListResponse)
async def list_threats(
    skip: int = 0,
    limit: int = 20,
    user=Depends(get_current_user),
) -> ThreatReportListResponse:
    return await inference_controller.list_threat_reports(skip, limit, str(user.id))


@router.get("/threats/{inference_id}", response_model=ThreatReportResponse)
async def get_threat_report(
    inference_id: str,
    user=Depends(get_current_user),
) -> ThreatReportResponse:
    return await inference_controller.get_threat_report(inference_id, str(user.id))
