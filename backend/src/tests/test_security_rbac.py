"""TC-SEC-01..04: RBAC — admin-only endpoints must reject regular users."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from middleware.dependencies import get_current_user

pytestmark = pytest.mark.asyncio


@pytest.fixture
def admin_user():
    user = MagicMock()
    user.id = "507f1f77bcf86cd799439011"
    user.email = "admin@test.com"
    user.role = "ADMIN"
    return user


@pytest.fixture
def regular_user():
    user = MagicMock()
    user.id = "507f1f77bcf86cd799439012"
    user.email = "regular@test.com"
    user.role = "USER"
    return user


@pytest.fixture
def app_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestSecurityRBAC:
    async def test_tc_sec_01_admin_can_create_invite(self, app_client, admin_user):
        app.dependency_overrides[get_current_user] = lambda: admin_user
        mock_invite = {"code": "abc123", "role": "ADMIN"}
        with patch(
            "modules.auth.controllers.auth_controller.create_invite",
            new_callable=AsyncMock,
            return_value=mock_invite,
        ):
            response = await app_client.post("/api/auth/invite")
            assert response.status_code == 200
            assert "invite" in response.json()
        app.dependency_overrides.clear()

    async def test_tc_sec_02_user_cannot_create_invite(self, app_client, regular_user):
        app.dependency_overrides[get_current_user] = lambda: regular_user
        response = await app_client.post("/api/auth/invite")
        assert response.status_code == 403
        assert "Acesso negado" in response.json().get("error", "")
        app.dependency_overrides.clear()

    async def test_tc_sec_03_user_cannot_start_training(self, app_client, regular_user):
        app.dependency_overrides[get_current_user] = lambda: regular_user
        response = await app_client.post("/api/training/train", json={"epochs": 1})
        assert response.status_code == 403
        assert "Acesso negado" in response.json().get("error", "")
        app.dependency_overrides.clear()

    async def test_tc_sec_04_user_cannot_activate_model(self, app_client, regular_user):
        app.dependency_overrides[get_current_user] = lambda: regular_user
        response = await app_client.post(
            "/api/training/models/activate",
            json={"model_id": "some-fake-id"},
        )
        assert response.status_code == 403
        assert "Acesso negado" in response.json().get("error", "")
        app.dependency_overrides.clear()
