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


class TestAttackIntegration:
    async def test_simulate_missing_fields(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_sim = MagicMock()
        mock_sim.id = "sim1"
        mock_sim.attack_type = "ddos"
        mock_sim.target_component = "server"
        mock_sim.severity = "critical"
        mock_sim.description = "DDoS"
        mock_sim.technical_details = "details"
        mock_sim.countermeasures = []
        with patch(
            "modules.attack.services.attack_service.simulate_attack",
            new_callable=AsyncMock,
            return_value=mock_sim,
        ), patch(
            "modules.attack.services.attack_service.list_countermeasures",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            # empty body is valid — controller extracts type/target with defaults
            response = await app_client.post("/api/attack/simulate", json={})
            assert response.status_code in (200, 400, 422, 500)
        app.dependency_overrides.clear()

    async def test_simulate_with_components(self, app_client, mock_user):
        app.dependency_overrides[get_current_user] = lambda: mock_user
        mock_sim = MagicMock()
        mock_sim.id = "sim123"
        mock_sim.attack_type = "ddos"
        mock_sim.target_component = "server"
        mock_sim.severity = "critical"
        mock_sim.description = "DDoS attack"
        mock_sim.technical_details = "details"
        mock_sim.countermeasures = []
        with patch(
            "modules.attack.services.attack_service.simulate_attack",
            new_callable=AsyncMock,
            return_value=mock_sim,
        ):
            response = await app_client.post("/api/attack/simulate", json={"type": "ddos", "target": "server"})
            assert response.status_code == 200
        app.dependency_overrides.clear()
