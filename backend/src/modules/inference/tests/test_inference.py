from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from middleware.dependencies import get_current_user

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "507f1f77bcf86cd799439011"
    return user


@pytest.fixture
def app(mock_user) -> FastAPI:
    from main import app

    app.dependency_overrides[get_current_user] = lambda: mock_user
    return app


def _make_mock_inference(**overrides):
    from datetime import datetime

    mock = MagicMock()
    mock.id = overrides.get("id", "inf1")
    mock.user_id = overrides.get("user_id", "user1")
    mock.filename = overrides.get("filename", "test.png")
    mock.image_path = overrides.get("image_path", "/tmp/test.png")
    mock.status = overrides.get("status", "completed")

    comp = MagicMock()
    comp.class_id = 0
    comp.label = "user"
    comp.confidence = 0.95
    comp.bbox = [10.0, 20.0, 90.0, 130.0]
    comp.inference_id = overrides.get("id", "inf1")
    mock.components = [comp]

    mock.processing_time_ms = 150.0
    mock.created_at = datetime(2026, 6, 9, 0, 0, 0)
    return mock


def _make_mock_threat_report(**overrides):
    from datetime import datetime

    from modules.inference.models.threat_model import (
        ComponentThreatAnalysis,
        Countermeasure,
        Threat,
        Vulnerability,
    )

    mock = MagicMock()
    mock.id = overrides.get("id", "tr1")
    mock.inference_id = overrides.get("inference_id", "inf1")
    mock.user_id = overrides.get("user_id", "user1")
    mock.status = "completed"
    mock.stride_summary = {"spoofing": 1, "tampering": 0, "repudiation": 1, "information_disclosure": 0, "denial_of_service": 0, "elevation_of_privilege": 0}
    mock.component_analyses = [
        ComponentThreatAnalysis(
            component_label="user",
            component_class_id=0,
            stride_threats=[
                Threat(category="spoofing", description="Falsificar identidade", risk_level="high"),
                Threat(category="repudiation", description="Negar ação", risk_level="medium"),
            ],
            vulnerabilities=[
                Vulnerability(cve_id="CWE-287", title="Improper Authentication", description="Falta de autenticação", cvss_score=8.1, cwe="CWE-287", affected_component="user"),
            ],
            countermeasures=[
                Countermeasure(title="Implementar MFA", description="Autenticação multifator", priority="critical", implementation_guide="Usar OAuth 2.0", references=["https://example.com"]),
            ],
        )
    ]
    mock.overall_risk_score = 5.0
    mock.created_at = datetime(2026, 6, 9, 0, 0, 0)
    mock.updated_at = datetime(2026, 6, 9, 0, 0, 0)
    return mock


class TestInferenceAnalyze:
    async def test_analyze_success(self, app: FastAPI):
        with patch(
            "modules.inference.services.inference_service.analyze_diagram",
            new_callable=AsyncMock,
            return_value=_make_mock_inference(id="test123"),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post("/api/inference/analyze", files={"file": ("d.png", b"data", "image/png")})
                assert r.status_code == 200
                assert r.json()["status"] == "completed"

    async def test_analyze_requires_auth(self, app: FastAPI):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/inference/analyze", files={"file": ("t.png", b"x", "image/png")})
            assert r.status_code == 401


class TestAnalyzeThreat:
    async def test_analyze_threat_success(self, app: FastAPI):
        mock_inference = _make_mock_inference(id="inf1")
        mock_inference.components = [
            MagicMock(class_id=0, label="user", confidence=0.95, bbox=[1, 2, 3, 4]),
            MagicMock(class_id=1, label="server", confidence=0.87, bbox=[5, 6, 7, 8]),
        ]

        mock_report = _make_mock_threat_report(inference_id="inf1")

        with patch(
            "modules.inference.services.inference_service.analyze_diagram",
            new_callable=AsyncMock,
            return_value=mock_inference,
        ), patch(
            "modules.inference.services.threat_service.analyze_threats",
            new_callable=AsyncMock,
            return_value=mock_report,
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post("/api/inference/analyze-threat", files={"file": ("d.png", b"data", "image/png")})
                assert r.status_code == 200
                data = r.json()
                assert "inference" in data
                assert "threat_report" in data
                assert data["threat_report"]["status"] == "completed"


class TestInferenceReports:
    async def test_list_reports_empty(self, app: FastAPI):
        with patch("modules.inference.services.inference_service.list_inferences", new_callable=AsyncMock, return_value=([], 0)):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/inference/reports")
                assert r.json()["total"] == 0

    async def test_list_reports_with_items(self, app: FastAPI):
        with patch("modules.inference.services.inference_service.list_inferences", new_callable=AsyncMock, return_value=([_make_mock_inference(id="inf1")], 1)):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/inference/reports")
                assert r.json()["total"] == 1

    async def test_get_report_found(self, app: FastAPI):
        with patch("modules.inference.services.inference_service.get_inference", new_callable=AsyncMock, return_value=_make_mock_inference(id="inf1")):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/inference/reports/inf1")
                assert r.json()["id"] == "inf1"

    async def test_get_report_not_found(self, app: FastAPI):
        with patch("modules.inference.services.inference_service.InferenceResult.get", new_callable=AsyncMock, return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                assert (await c.get("/api/inference/reports/nonexistent")).status_code == 404


class TestThreatReports:
    async def test_list_threat_reports(self, app: FastAPI):
        with patch("modules.inference.services.threat_service.list_threat_reports", new_callable=AsyncMock, return_value=([_make_mock_threat_report()], 1)):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/inference/threats")
                assert r.json()["total"] == 1

    async def test_get_threat_report_found(self, app: FastAPI):
        with patch("modules.inference.services.threat_service.get_threat_report_by_inference", new_callable=AsyncMock, return_value=_make_mock_threat_report()):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/inference/threats/inf1")
                assert r.status_code == 200
                data = r.json()
                assert data["inference_id"] == "inf1"
                assert data["stride_summary"]["spoofing"] == 1
                assert len(data["component_analyses"]) == 1
                assert data["component_analyses"][0]["component_label"] == "user"

    async def test_get_threat_report_not_found(self, app: FastAPI):
        with patch("modules.inference.services.threat_service.get_threat_report_by_inference", new_callable=AsyncMock, return_value=None):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                assert (await c.get("/api/inference/threats/nonexistent")).status_code == 404
