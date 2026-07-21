from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from middleware.dependencies import get_current_user
from modules.inference.dataset.dataset_model import DatasetEntry

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


def _make_mock_entry(**overrides):
    from datetime import datetime
    mock = MagicMock()
    mock.id = overrides.get("id", "entry1")
    mock.user_id = overrides.get("user_id", "user1")
    mock.filename = overrides.get("filename", "diagram.png")
    mock.image_path = "/tmp/dataset/diagram.png"
    mock.labels = [
        MagicMock(class_id=0, label="user", x_center=0.5, y_center=0.5, width=0.1, height=0.1)
    ]
    mock.source = overrides.get("source", "manual")
    mock.split = overrides.get("split", "train")
    mock.augmented = overrides.get("augmented", False)
    mock.image_width = 640
    mock.image_height = 640
    mock.created_at = datetime(2026, 6, 9, 0, 0, 0)
    return mock


class TestDatasetUpload:
    async def test_upload_success(self, app: FastAPI):
        with patch(
            "modules.inference.dataset.dataset_controller.dataset_service.upload_entry",
            new_callable=AsyncMock,
            return_value=_make_mock_entry(),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post(
                    "/api/dataset/upload",
                    files={"file": ("d.png", b"data", "image/png")},
                    data={"labels": '[{"class_id":0,"label":"user","x_center":0.5,"y_center":0.5,"width":0.1,"height":0.1}]', "split": "train"},
                )
                assert r.status_code == 200
                assert r.json()["labels"][0]["label"] == "user"

    async def test_upload_requires_auth(self, app: FastAPI):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.post("/api/dataset/upload", files={"file": ("t.png", b"x", "image/png")}, data={"labels": "[]"})
            assert r.status_code == 401


class TestDatasetEntries:
    async def test_list_entries(self, app: FastAPI):
        with patch(
            "modules.inference.dataset.dataset_service.list_entries",
            new_callable=AsyncMock,
            return_value=([_make_mock_entry()], 1),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/dataset/entries")
                assert r.status_code == 200
                data = r.json()
                assert data["total"] == 1
                assert len(data["items"]) == 1
                assert data["items"][0]["labels"][0]["label"] == "user"

    async def test_list_entries_empty(self, app: FastAPI):
        with patch(
            "modules.inference.dataset.dataset_service.list_entries",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/dataset/entries")
                assert r.json()["total"] == 0

    async def test_delete_entry(self, app: FastAPI):
        with patch("os.remove"), patch(
            "modules.inference.dataset.dataset_service.DatasetEntry.get",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_entry = MagicMock(spec=DatasetEntry)
            mock_entry.image_path = "/tmp/test.png"
            mock_entry.delete = AsyncMock()
            mock_get.return_value = mock_entry

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.delete("/api/dataset/entries/entry1")
                assert r.json()["deleted"] is True

    async def test_delete_entry_not_found(self, app: FastAPI):
        with patch(
            "modules.inference.dataset.dataset_service.DatasetEntry.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.delete("/api/dataset/entries/nonexistent")
                assert r.json()["deleted"] is False


class TestDatasetAugment:
    async def test_augment_entry_success(self, app: FastAPI):
        mock_results = [
            _make_mock_entry(id="aug1", augmented=True, source="augmented"),
            _make_mock_entry(id="aug2", augmented=True, source="augmented"),
        ]

        with patch(
            "modules.inference.dataset.dataset_controller.dataset_service.augment_entry",
            new_callable=AsyncMock,
            return_value=mock_results,
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post("/api/dataset/entries/entry1/augment")
                assert r.status_code == 200
                data = r.json()
                assert data["total"] == 2

    async def test_augment_entry_not_found(self, app: FastAPI):
        with patch(
            "modules.inference.dataset.dataset_service.DatasetEntry.get",
            new_callable=AsyncMock,
            return_value=None,
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.post("/api/dataset/entries/nonexistent/augment")
                assert r.status_code == 200
                assert r.json()["total"] == 0


class TestDatasetStats:
    async def test_get_stats(self, app: FastAPI):
        with patch(
            "modules.inference.dataset.dataset_service.get_stats",
            new_callable=AsyncMock,
            return_value={
                "total": 10,
                "train_count": 7,
                "val_count": 2,
                "test_count": 1,
                "manual_count": 8,
                "augmented_count": 2,
                "label_distribution": {"user": 5, "server": 3, "database": 2},
            },
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/dataset/stats")
                assert r.status_code == 200
                data = r.json()
                assert data["total"] == 10
                assert data["train_count"] == 7
                assert data["label_distribution"]["user"] == 5
