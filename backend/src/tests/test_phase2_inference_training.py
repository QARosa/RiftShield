"""
Fase 2 — Novos casos de teste:
  TC-INF-05: POST /inference/compare   — comparação de duas arquiteturas
  TC-INF-06: POST /inference/suggest   — sugestão de melhoria de arquitetura
  TC-TR-03:  POST /training/fine-tune  — validação de payload fine-tune
"""
from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from middleware.dependencies import get_current_user

pytestmark = pytest.mark.asyncio

_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16  # minimal PNG-like header


@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = "507f1f77bcf86cd799439011"
    user.language = "pt-BR"
    return user


@pytest.fixture
def app_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


def _make_mock_inference(**kwargs):
    inf = MagicMock()
    inf.id = kwargs.get("id", "inf1")
    inf.filename = kwargs.get("filename", "arch.png")
    inf.status = "completed"
    inf.components = kwargs.get("components", [MagicMock(class_id=0, label="api", confidence=0.9, bbox=[0, 0, 10, 10])])
    inf.processing_time_ms = 100
    inf.fallback_used = False
    inf.created_at = datetime(2026, 1, 1)
    inf.insert = AsyncMock()
    return inf


def _make_mock_threat(inf=None):
    t = MagicMock()
    t.id = "thr1"
    t.inference_id = getattr(inf, "id", "inf1") if inf else "inf1"
    t.threats = []
    t.created_at = datetime(2026, 1, 1)
    return t


# ---------------------------------------------------------------------------
# TC-INF-05 — Compare architectures
# ---------------------------------------------------------------------------
class TestCompareArchitectures:
    async def test_compare_returns_comparison_result(self, app_client, mock_user):
        """TC-INF-05: dois uploads → resultado de comparação com diff."""
        app.dependency_overrides[get_current_user] = lambda: mock_user

        inf_a = _make_mock_inference(id="inf_a", filename="arch_a.png")
        inf_b = _make_mock_inference(id="inf_b", filename="arch_b.png")
        thr_a = _make_mock_threat(inf_a)
        thr_b = _make_mock_threat(inf_b)

        mock_comparison_log = MagicMock()
        mock_comparison_log.insert = AsyncMock()

        compare_result = {
            "summary": "Arquitetura B tem mais componentes",
            "added": ["database"],
            "removed": [],
            "common": ["api"],
        }

        with patch(
            "modules.inference.controllers.inference_controller.inference_service.analyze_diagram",
            new_callable=AsyncMock,
            side_effect=[inf_a, inf_b],
        ), patch(
            "modules.inference.controllers.inference_controller._get_llm_config",
            new_callable=AsyncMock,
            return_value={},
        ), patch(
            "modules.inference.controllers.inference_controller.threat_service.analyze_threats",
            new_callable=AsyncMock,
            side_effect=[thr_a, thr_b],
        ), patch(
            "modules.inference.services.comparison_service.compare_architectures",
            new_callable=AsyncMock,
            return_value=compare_result,
        ), patch(
            "modules.inference.models.comparison_model.ComparisonLog",
        ) as MockCLog:
            mock_log_inst = MagicMock()
            mock_log_inst.insert = AsyncMock()
            MockCLog.return_value = mock_log_inst
            response = await app_client.post(
                "/api/inference/compare",
                files={
                    "file_a": ("arch_a.png", _PNG, "image/png"),
                    "file_b": ("arch_b.png", _PNG, "image/png"),
                },
            )
            assert response.status_code in (200, 201)
            data = response.json()
            assert isinstance(data, dict)

        app.dependency_overrides.clear()

    async def test_compare_missing_files(self, app_client, mock_user):
        """TC-INF-05 (negativo): sem arquivos → 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        response = await app_client.post("/api/inference/compare")
        assert response.status_code == 422
        app.dependency_overrides.clear()

    async def test_compare_single_file(self, app_client, mock_user):
        """TC-INF-05 (negativo): apenas um arquivo → 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        response = await app_client.post(
            "/api/inference/compare",
            files={"file_a": ("arch_a.png", _PNG, "image/png")},
        )
        assert response.status_code == 422
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# TC-INF-06 — Suggest architecture
# ---------------------------------------------------------------------------
class TestSuggestArchitecture:
    async def test_suggest_returns_suggestions(self, app_client, mock_user):
        """TC-INF-06: dois uploads → sugestões de melhoria."""
        app.dependency_overrides[get_current_user] = lambda: mock_user

        suggest_result = {
            "suggestions": ["Adicionar WAF", "Separar banco de leitura/escrita"],
            "rationale": "Baseado nos componentes detectados",
        }

        with patch(
            "modules.inference.controllers.inference_controller.suggest_architecture",
            new_callable=AsyncMock,
            return_value=suggest_result,
        ):
            class _FakeComparisonLog:
                created_at = MagicMock()

                @classmethod
                async def find_one(cls, *a, **kw):
                    return None

            with patch(
                "modules.inference.models.comparison_model.ComparisonLog",
                new=_FakeComparisonLog,
            ):
                response = await app_client.post(
                    "/api/inference/suggest",
                    files={
                        "file_a": ("arch_a.png", _PNG, "image/png"),
                        "file_b": ("arch_b.png", _PNG, "image/png"),
                    },
                )
                assert response.status_code in (200, 201)
                data = response.json()
                assert isinstance(data, dict)

        app.dependency_overrides.clear()

    async def test_suggest_missing_files(self, app_client, mock_user):
        """TC-INF-06 (negativo): sem arquivos → 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        response = await app_client.post("/api/inference/suggest")
        assert response.status_code == 422
        app.dependency_overrides.clear()

    async def test_suggest_unauthenticated(self, app_client):
        """TC-INF-06 (negativo): sem autenticação → 401."""
        from shared.utils.errors import UnauthorizedError
        app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(UnauthorizedError())
        response = await app_client.post(
            "/api/inference/suggest",
            files={
                "file_a": ("a.png", _PNG, "image/png"),
                "file_b": ("b.png", _PNG, "image/png"),
            },
        )
        assert response.status_code == 401
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# TC-TR-03 — Fine-tune endpoint
# ---------------------------------------------------------------------------
class TestFineTune:
    def _make_log(self, **kwargs):
        log = MagicMock()
        log.id = "log1"
        log.model_type = "yolov8n"
        log.dataset_version = "latest"
        log.hyperparameters = {"epochs": kwargs.get("epochs", 5)}
        # metrics must be a dict so pydantic coerces to TrainingMetricsResponse
        log.metrics = {
            "mAP50": None, "mAP50_95": None, "precision": None,
            "recall": None, "f1_score": None, "epochs_completed": None, "error": None,
        }
        log.model_path = None
        log.status = "queued"
        log.started_at = None
        log.completed_at = None
        log.created_at = datetime(2026, 1, 1)
        return log

    async def test_fine_tune_default_epochs(self, app_client, mock_user):
        """TC-TR-03: POST /fine-tune sem corpo → usa epochs=10 default."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        with patch(
            "modules.inference.controllers.training_controller.training_service.fine_tune",
            new_callable=AsyncMock,
            return_value=self._make_log(epochs=10),
        ):
            response = await app_client.post("/api/training/fine-tune", json={})
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
        app.dependency_overrides.clear()

    async def test_fine_tune_custom_epochs(self, app_client, mock_user):
        """TC-TR-03: POST /fine-tune com epochs customizado."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        with patch(
            "modules.inference.controllers.training_controller.training_service.fine_tune",
            new_callable=AsyncMock,
            return_value=self._make_log(epochs=25),
        ):
            response = await app_client.post("/api/training/fine-tune", json={"epochs": 25})
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "queued"
        app.dependency_overrides.clear()

    async def test_fine_tune_invalid_payload(self, app_client, mock_user):
        """TC-TR-03 (negativo): epochs como string → 422."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
        response = await app_client.post("/api/training/fine-tune", json={"epochs": "invalid"})
        assert response.status_code == 422
        app.dependency_overrides.clear()

    async def test_fine_tune_unauthenticated(self, app_client):
        """TC-TR-03 (negativo): sem auth → 401."""
        from shared.utils.errors import UnauthorizedError
        app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(UnauthorizedError())
        response = await app_client.post("/api/training/fine-tune", json={"epochs": 5})
        assert response.status_code == 401
        app.dependency_overrides.clear()
