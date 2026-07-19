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


def _make_mock_log(**overrides):
    from datetime import datetime
    mock = MagicMock()
    mock.id = overrides.get("id", "log1")
    mock.model_type = overrides.get("model_type", "yolov8n")
    mock.dataset_version = "latest"
    mock.hyperparameters = {"epochs": 100}
    mock.metrics = overrides.get("metrics", {"mAP50": 0.85})
    mock.model_path = "/tmp/best.pt"
    mock.status = overrides.get("status", "completed")
    mock.started_at = datetime(2026, 6, 9, 0, 0, 0)
    mock.completed_at = datetime(2026, 6, 9, 1, 0, 0)
    mock.created_at = datetime(2026, 6, 9, 0, 0, 0)
    return mock


class TestTraining:
    async def test_start_training(self, app: FastAPI):
        with patch(
            "modules.inference.controllers.training_controller.training_service.fine_tune",
            new_callable=AsyncMock,
            return_value=_make_mock_log(status="completed"),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post(
                    "/api/training/train",
                    json={"model_type": "yolov8n", "epochs": 10},
                )
                assert r.status_code == 200
                data = r.json()
                assert data["status"] == "completed"
                assert data["model_type"] == "yolov8n"

    async def test_start_training_requires_auth(self, app: FastAPI):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/training/train", json={})
            assert r.status_code == 401

    async def test_list_models(self, app: FastAPI):
        with patch(
            "modules.inference.services.training_service.list_training_logs",
            new_callable=AsyncMock,
            return_value=([_make_mock_log()], 1),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/training/models")
                assert r.status_code == 200
                data = r.json()
                assert data["total"] == 1
                assert data["items"][0]["model_type"] == "yolov8n"

    async def test_list_models_empty(self, app: FastAPI):
        with patch(
            "modules.inference.services.training_service.list_training_logs",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/training/models")
                assert r.json()["total"] == 0

    async def test_get_model_found(self, app: FastAPI):
        with patch(
            "modules.inference.services.training_service.get_training_log",
            new_callable=AsyncMock,
            return_value=_make_mock_log(),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/training/models/log1")
                assert r.json()["id"] == "log1"

    async def test_get_model_not_found(self, app: FastAPI):
        with patch(
            "modules.inference.services.training_service.TrainingLog.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/training/models/nonexistent")
                assert r.status_code == 404

    async def test_activate_model(self, app: FastAPI):
        with patch(
            "modules.inference.services.inference_service.set_active_model",
        ) as mock_set:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post(
                    "/api/training/models/activate",
                    json={"model_path": "/tmp/best.pt"},
                )
                assert r.json()["activated"] is True
                mock_set.assert_called_once_with("/tmp/best.pt")
