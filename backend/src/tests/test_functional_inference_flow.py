import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch

from main import app
from middleware.dependencies import get_current_user


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "507f1f77bcf86cd799439011"
    return user


@pytest.fixture
def app_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestInferenceFunctionalFlow:
    """Fluxo funcional completo: upload -> análise -> threat report -> export"""

    async def test_full_inference_flow(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user

        from datetime import datetime
        files = {"file": ("diagram.png", b"fake-image-data", "image/png")}
        mock_inf = MagicMock()
        mock_inf.id = "inf123"
        mock_inf.filename = "diagram.png"
        mock_inf.status = "completed"
        mock_inf.components = [MagicMock(class_id=0, label="api", confidence=0.9, bbox=[0, 0, 10, 10])]
        mock_inf.processing_time_ms = 100
        mock_inf.fallback_used = False
        mock_inf.created_at = datetime(2026, 1, 1)
        mock_inf.insert = AsyncMock()

        with patch(
            "modules.inference.controllers.inference_controller.inference_service.analyze_diagram",
            new_callable=AsyncMock,
            return_value=mock_inf,
        ):
            response = await app_client.post("/api/inference/analyze", files=files)
            assert response.status_code in (200, 201)
            data = response.json()
            assert "components" in data or "id" in data

        app.dependency_overrides.clear()

    async def test_export_all_formats(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user

        with patch("modules.export.services.export_service._get_inferences", new_callable=AsyncMock) as mock_inf:
            mock_inf.return_value = [{"id": "1", "filename": "test.png", "status": "completed", "components": [], "processing_time_ms": 100, "fallback_used": False, "created_at": "2026-01-01"}]
            with patch("modules.export.services.export_service._get_threats", new_callable=AsyncMock) as mock_thr:
                mock_thr.return_value = []
                with patch("modules.export.services.export_service._get_dataset", new_callable=AsyncMock) as mock_ds:
                    mock_ds.return_value = []
                    with patch("modules.export.services.export_service._get_vulnerabilities", new_callable=AsyncMock) as mock_vuln:
                        mock_vuln.return_value = []
                        with patch("modules.export.services.export_service._get_countermeasures", new_callable=AsyncMock) as mock_cm:
                            mock_cm.return_value = []

                            for fmt in ["json", "csv"]:
                                response = await app_client.post("/api/export/export", json={
                                    "sections": ["inferences"],
                                    "format": fmt,
                                    "zip": False,
                                })
                                assert response.status_code == 200
                                data = response.json()
                                assert "filename" in data
                                assert data["filename"].endswith(f".{fmt}")

        app.dependency_overrides.clear()

    async def test_export_zip(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        with patch("modules.export.services.export_service._get_inferences", new_callable=AsyncMock) as mock_inf:
            mock_inf.return_value = []
            response = await app_client.post("/api/export/export", json={
                "sections": ["inferences"],
                "format": "json",
                "zip": True,
            })
            assert response.status_code == 200
            data = response.json()
            assert "filename" in data
            assert data["filename"].endswith(".zip")
        app.dependency_overrides.clear()
