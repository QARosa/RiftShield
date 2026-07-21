import os

import pytest

from config.settings import get_settings


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    get_settings.cache_clear()
    db_url = os.getenv(
        "DATABASE_URL",
        "mongodb://127.0.0.1:27020/riftshield_test",
    )
    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("JWT_SECRET", os.getenv("JWT_SECRET", "test-secret-minimum-32-characters-long"))
    monkeypatch.setenv(
        "JWT_REFRESH_SECRET",
        os.getenv("JWT_REFRESH_SECRET", "test-refresh-secret-minimum-32-chars"),
    )
    settings = get_settings()
    settings.database_url = db_url
    yield
