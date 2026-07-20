import bcrypt
import pytest
from httpx import AsyncClient

from modules.auth.models.user_model import User

# Mark all tests in this module as async, as they interact with the database and API
pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
async def regular_user():
    """
    Fixture to create a regular user with 'USER' role for testing RBAC.
    This user is created once per module and cleaned up afterwards.
    """
    # Clean up any previous user with this email to ensure a clean state
    await User.find_one(User.email == "regular@test.com").delete()

    hashed_password = bcrypt.hashpw("test123".encode("utf-8"), bcrypt.gensalt())
    user = User(
        name="Regular User",
        email="regular@test.com",
        hashed_password=hashed_password.decode("utf-8"),
        role="USER",  # Explicitly a regular user
        is_active=True,
    )
    await user.insert()
    yield user
    # Teardown: remove the user after tests in the module are done
    await user.delete()


async def test_tc_sec_01_admin_can_create_invite(client: AsyncClient):
    """
    TC-SEC-01: Validates that an authenticated ADMIN user can create an invite code.
    """
    # 1. Login as the admin user (created by the seed script)
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "test@riftshield.com", "password": "test123"},
    )
    assert login_response.status_code == 200, "Admin login failed"

    # 2. Attempt to create an invite code
    invite_response = await client.post("/api/auth/invite")

    # 3. Assert that the request was successful
    assert invite_response.status_code == 200
    response_data = invite_response.json()
    assert "invite" in response_data and "code" in response_data["invite"]


async def test_tc_sec_02_user_cannot_create_invite(client: AsyncClient, regular_user: User):
    """
    TC-SEC-02: Validates that a regular USER cannot access an admin-only endpoint.
    """
    # 1. Login as the regular user created by the fixture
    login_response = await client.post(
        "/api/auth/login",
        json={"email": regular_user.email, "password": "test123"},
    )
    assert login_response.status_code == 200, "Regular user login failed"

    # 2. Attempt to create an invite code (which should be forbidden)
    invite_response = await client.post("/api/auth/invite")

    # 3. Assert that access is denied with a 403 Forbidden status
    assert invite_response.status_code == 403
    response_data = invite_response.json()
    assert "Acesso negado" in response_data.get("detail", "")


async def test_tc_sec_03_user_cannot_start_training(client: AsyncClient, regular_user: User):
    """
    TC-SEC-03: Validates that a regular USER cannot start a training job.
    """
    # 1. Login as the regular user
    login_response = await client.post(
        "/api/auth/login",
        json={"email": regular_user.email, "password": "test123"},
    )
    assert login_response.status_code == 200, "Regular user login failed"

    # 2. Attempt to start a training job (which should be forbidden)
    training_response = await client.post("/api/training/train", json={"epochs": 1})

    # 3. Assert that access is denied with a 403 Forbidden status
    assert training_response.status_code == 403
    response_data = training_response.json()
    assert "Acesso negado" in response_data.get("detail", "")


async def test_tc_sec_04_user_cannot_activate_model(client: AsyncClient, regular_user: User):
    """
    TC-SEC-04: Validates that a regular USER cannot activate a model.
    """
    # 1. Login as the regular user
    login_response = await client.post(
        "/api/auth/login",
        json={"email": regular_user.email, "password": "test123"},
    )
    assert login_response.status_code == 200, "Regular user login failed"

    # 2. Attempt to activate a model (which should be forbidden)
    activate_response = await client.post("/api/training/models/activate", json={"model_id": "some-fake-id"})

    # 3. Assert that access is denied with a 403 Forbidden status
    assert activate_response.status_code == 403
    response_data = activate_response.json()
    assert "Acesso negado" in response_data.get("detail", "")