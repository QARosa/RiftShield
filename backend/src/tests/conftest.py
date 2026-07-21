from unittest.mock import MagicMock

import pytest


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
