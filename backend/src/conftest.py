import asyncio

import pytest

from config.settings import get_settings


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def override_settings():
    settings = get_settings()
    settings.database_url = "mongodb://localhost:27017/test_riftshield"
    yield
