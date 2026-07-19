import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from main import app
from middleware.dependencies import get_current_user
from modules.auth.models.user_model import User


pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.name = "Test User"
    user.email = "test@example.com"
    user.phone = "71999999999"
    user.country = "Brasil"
    user.state = "Bahia"
    user.city = "Salvador"
    user.role = "user"
    user.profession = "Arquiteto"
    user.seniority = "senior"
    user.age = 30
    user.language = "pt-BR"
    user.total_days_active = 10
    user.total_seconds_active = 3600
    user.custom_cursor_enabled = True
    user.user_id = "507f1f77bcf86cd799439011"
    user.save = AsyncMock()
    user.refresh_token = "mock-refresh-token"
    return user


@pytest.fixture
def app_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestAuthIntegration:
    async def test_health_check(self, app_client):
        response = await app_client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_login_missing_fields(self, app_client):
        response = await app_client.post("/api/auth/login", json={})
        assert response.status_code in (400, 422)

    async def test_login_invalid_credentials(self, app_client):
        with patch("modules.auth.services.auth_service.User.find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            response = await app_client.post("/api/auth/login", json={"email": "nonexistent@test.com", "password": "123456"})
            assert response.status_code == 401

    async def test_register_missing_fields(self, app_client):
        response = await app_client.post("/api/auth/register", json={})
        assert response.status_code in (400, 422)

    async def test_refresh_no_token(self, app_client):
        response = await app_client.post("/api/auth/refresh")
        assert response.status_code in (401, 422)

    async def test_logout(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        with patch("modules.auth.services.auth_service.User.get", new_callable=AsyncMock, return_value=mock_user):
            response = await app_client.post("/api/auth/logout")
            assert response.status_code == 200
        app.dependency_overrides.clear()

    async def test_get_profile_authenticated(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        from datetime import datetime
        mock_user.created_at = datetime(2026, 1, 1)
        with patch("modules.auth.services.auth_service.User.get", new_callable=AsyncMock, return_value=mock_user):
            response = await app_client.get("/api/users/me")
            assert response.status_code == 200
            data = response.json()
            assert "user" in data
        app.dependency_overrides.clear()

    async def test_get_profile_unauthenticated(self, app_client):
        from shared.utils.errors import UnauthorizedError
        app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(UnauthorizedError())
        response = await app_client.get("/api/users/me")
        assert response.status_code == 401
        app.dependency_overrides.clear()

    async def test_usage_tick_authenticated(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_user.save = AsyncMock()
        with patch("modules.auth.models.user_model.User.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_user
            response = await app_client.post("/api/users/usage-tick")
            assert response.status_code == 200
            assert response.json() == {"ok": True}
        app.dependency_overrides.clear()

    async def test_usage_time_authenticated(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        with patch("modules.auth.models.user_model.User.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_user
            response = await app_client.get("/api/users/usage-time")
            assert response.status_code == 200
            data = response.json()
            assert "total_seconds" in data
            assert "hours" in data
            assert "minutes" in data
            assert "seconds" in data
        app.dependency_overrides.clear()

    # TC-AUTH-05: Admin generates invite code
    async def test_generate_invite_as_admin(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_invite = MagicMock()
        mock_invite.code = "test-invite-code-abc"
        mock_invite.role = "user"
        with patch(
            "modules.auth.services.invite_service.Invite.insert",
            new_callable=AsyncMock,
        ), patch(
            "modules.auth.controllers.auth_controller.create_invite",
            new_callable=AsyncMock,
            return_value=mock_invite,
        ):
            response = await app_client.post("/api/auth/invite")
            assert response.status_code == 200
            data = response.json()
            assert "invite" in data
        app.dependency_overrides.clear()

    # TC-AUTH-05 (negative): Unauthenticated request to /invite → 401
    async def test_generate_invite_unauthenticated(self, app_client):
        from shared.utils.errors import UnauthorizedError
        app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(UnauthorizedError())
        response = await app_client.post("/api/auth/invite")
        assert response.status_code == 401
        app.dependency_overrides.clear()

    # TC-AUTH-06: Authenticated user updates profile
    async def test_update_profile(self, app_client, mock_user):
        from datetime import datetime
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_user.created_at = datetime(2026, 1, 1)
        updated_mock = MagicMock(spec=User)
        updated_mock.id = mock_user.id
        updated_mock.name = "Updated Name"
        updated_mock.email = mock_user.email
        updated_mock.phone = "71888888888"
        updated_mock.country = "Brasil"
        updated_mock.state = "Bahia"
        updated_mock.city = "Salvador"
        updated_mock.role = "user"
        updated_mock.profession = "Engenheiro"
        updated_mock.seniority = "senior"
        updated_mock.age = 31
        updated_mock.language = "pt-BR"
        updated_mock.total_days_active = 10
        updated_mock.total_seconds_active = 3600
        updated_mock.custom_cursor_enabled = True
        updated_mock.created_at = datetime(2026, 1, 1)
        with patch(
            "modules.auth.services.auth_service.User.get",
            new_callable=AsyncMock,
            return_value=mock_user,
        ):
            mock_user.save = AsyncMock()
            with patch(
                "modules.auth.services.auth_service.get_profile",
                new_callable=AsyncMock,
            ) as mock_profile:
                from modules.auth.schemas.auth_schema import UserResponse
                mock_profile.return_value = UserResponse(
                    id=str(mock_user.id),
                    name="Updated Name",
                    email=mock_user.email,
                    phone="71888888888",
                    country="Brasil",
                    state="Bahia",
                    city="Salvador",
                    role="user",
                    profession="Engenheiro",
                    seniority="senior",
                    age=31,
                    total_days_active=10,
                    total_seconds_active=3600,
                    language="pt-BR",
                    custom_cursor_enabled=True,
                )
                response = await app_client.put(
                    "/api/users/me",
                    json={"name": "Updated Name", "phone": "71888888888"},
                )
                assert response.status_code == 200
                data = response.json()
                assert "user" in data
        app.dependency_overrides.clear()
