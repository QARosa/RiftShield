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


def _make_mock_vuln(**overrides):
    from datetime import datetime
    mock = MagicMock()
    mock.id = overrides.get("id", "vuln1")
    mock.cve_id = overrides.get("cve_id", "CWE-89")
    mock.title = "SQL Injection"
    mock.title_pt = "Injeção SQL"
    mock.title_en = "SQL Injection"
    mock.description = "Test description"
    mock.description_pt = "Descrição de teste"
    mock.description_en = "Test description"
    mock.cvss_score = 9.0
    mock.cwe = "CWE-89"
    mock.affected_components = ["api", "database"]
    mock.tags = ["injection"]
    mock.created_at = datetime(2026, 6, 9, 0, 0, 0)
    return mock


def _make_mock_countermeasure(**overrides):
    from datetime import datetime
    mock = MagicMock()
    mock.id = overrides.get("id", "cm1")
    mock.title = "Parameterized Queries"
    mock.title_pt = "Consultas Parametrizadas"
    mock.title_en = "Parameterized Queries"
    mock.description = "Use parameterized queries"
    mock.description_pt = "Use consultas parametrizadas"
    mock.description_en = "Use parameterized queries"
    mock.priority = "critical"
    mock.implementation_guide = "Use ORM"
    mock.implementation_guide_pt = "Use ORM"
    mock.implementation_guide_en = "Use ORM"
    mock.references = ["https://example.com"]
    mock.vulnerability_cwe_ids = ["CWE-89"]
    mock.created_at = datetime(2026, 6, 9, 0, 0, 0)
    return mock


class TestKBVulnerabilities:
    async def test_list_vulnerabilities(self, app: FastAPI):
        with patch(
            "modules.inference.controllers.kb_controller.kb_service.list_vulnerabilities",
            new_callable=AsyncMock,
            return_value=([_make_mock_vuln()], 1),
        ) as mock_svc:
            mock_svc.return_value = ([_make_mock_vuln()], 1)
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/kb/vulnerabilities")
                assert r.status_code == 200
                data = r.json()
                assert data["total"] == 1
                assert data["items"][0]["cve_id"] == "CWE-89"

    async def test_list_vulnerabilities_filtered(self, app: FastAPI):
        with patch(
            "modules.inference.controllers.kb_controller.kb_service.list_vulnerabilities",
            new_callable=AsyncMock,
            return_value=([_make_mock_vuln()], 1),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/kb/vulnerabilities?component=api&min_cvss=5")
                assert r.status_code == 200

    async def test_list_vulnerabilities_empty(self, app: FastAPI):
        with patch(
            "modules.inference.controllers.kb_controller.kb_service.list_vulnerabilities",
            new_callable=AsyncMock,
            return_value=([], 0),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/kb/vulnerabilities")
                assert r.json()["total"] == 0

    async def test_list_vulnerabilities_requires_auth(self, app: FastAPI):
        app.dependency_overrides.clear()
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            r = await c.get("/api/kb/vulnerabilities")
            assert r.status_code == 401


class TestKBCountermeasures:
    async def test_list_countermeasures(self, app: FastAPI):
        with patch(
            "modules.inference.controllers.kb_controller.kb_service.list_countermeasures",
            new_callable=AsyncMock,
            return_value=([_make_mock_countermeasure()], 1),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/kb/countermeasures")
                assert r.status_code == 200
                data = r.json()
                assert data["total"] == 1
                # title field returns title_pt when lang=pt-BR (default)
                assert data["items"][0]["title"] in ("Parameterized Queries", "Consultas Parametrizadas")

    async def test_list_countermeasures_filtered(self, app: FastAPI):
        with patch(
            "modules.inference.controllers.kb_controller.kb_service.list_countermeasures",
            new_callable=AsyncMock,
            return_value=([_make_mock_countermeasure()], 1),
        ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", cookies={"accessToken": "x"}) as c:
                r = await c.get("/api/kb/countermeasures?cwe=CWE-89")
                assert r.status_code == 200
