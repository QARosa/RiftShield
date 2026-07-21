import asyncio
import pytest
from unittest.mock import MagicMock

from middleware.dependencies import get_current_user


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mongodb://localhost:27017/test_riftshield")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_REFRESH_SECRET", "test-refresh-secret")
    monkeypatch.setenv("FRONTEND_URL", "http://localhost:1999")


@pytest.fixture
def mock_user():
    user = MagicMock()
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
    return user


@pytest.fixture
def override_dependency(app, mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()
