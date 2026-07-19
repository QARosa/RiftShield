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
    user.name = "Test User"
    user.email = "test@example.com"
    return user


@pytest.fixture
def app_client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


class TestHermesIntegration:
    async def test_get_config_authenticated(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_config = MagicMock()
        mock_config.enabled = True
        mock_config.provider = "google"
        mock_config.google_api_key = "test-key"
        mock_config.openai_api_key = ""
        mock_config.deepseek_api_key = ""
        mock_config.google_model = "gemini-2.5-flash-lite"
        mock_config.openai_model = "gpt-4o-mini"
        mock_config.deepseek_model = "deepseek-chat"
        mock_config.diag_fallback = "yolo+hermes"
        mock_config.fallback_enabled = True
        with patch("modules.hermes.controllers.hermes_controller.HermesConfig") as MockHC:
            MockHC.find_one = AsyncMock(return_value=mock_config)
            response = await app_client.get("/api/hermes/config")
            assert response.status_code == 200
            data = response.json()
            assert "enabled" in data
        app.dependency_overrides.clear()

    async def test_get_config_no_config(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        with patch("modules.hermes.controllers.hermes_controller.HermesConfig") as MockHC:
            MockHC.find_one = AsyncMock(return_value=None)
            response = await app_client.get("/api/hermes/config")
            assert response.status_code == 200
            data = response.json()
            assert data.get("enabled") is True  # default when no config exists
        app.dependency_overrides.clear()

    async def test_save_config(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_instance = MagicMock()
        mock_instance.insert = AsyncMock()
        mock_instance.save = AsyncMock()
        with patch("modules.hermes.controllers.hermes_controller.HermesConfig") as MockHC:
            MockHC.find_one = AsyncMock(return_value=None)
            MockHC.return_value = mock_instance
            response = await app_client.put("/api/hermes/config", json={"enabled": True, "provider": "google"})
            assert response.status_code == 200
        app.dependency_overrides.clear()

    async def test_chat_without_message(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user

        class _FakeHermesConfig:
            user_id = MagicMock()

            @classmethod
            async def find_one(cls, *a, **kw):
                return None

        with patch(
            "modules.hermes.controllers.hermes_controller.HermesConfig",
            new=_FakeHermesConfig,
        ):
            response = await app_client.post("/api/hermes/chat", json={})
            assert response.status_code in (200, 400, 422)
        app.dependency_overrides.clear()
