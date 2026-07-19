import pytest
import bcrypt
from unittest.mock import AsyncMock, MagicMock, patch

from shared.utils.errors import AppError


class TestPasswordHashing:
    def test_hash_produces_valid_bcrypt_string(self):
        raw = "senha123"
        hashed = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        assert hashed.startswith("$2b$")
        assert len(hashed) > 20

    def test_correct_password_passes_check(self):
        raw = "senha123"
        hashed = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        assert bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))

    def test_wrong_password_fails_check(self):
        raw = "senha123"
        hashed = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        assert not bcrypt.checkpw("errada".encode("utf-8"), hashed.encode("utf-8"))

    def test_different_salts_produce_different_hashes(self):
        raw = "senha123"
        h1 = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        h2 = bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        assert h1 != h2


class TestInviteService:
    @pytest.mark.asyncio
    async def test_validate_invite_missing_raises_app_error(self):
        with patch("modules.auth.services.invite_service.Invite.find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = None
            from modules.auth.services.invite_service import validate_and_use_invite
            with pytest.raises(AppError) as exc_info:
                await validate_and_use_invite("nonexistent")
            assert exc_info.value.status_code == 403
            assert "inválido" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_validate_invite_used_raises_app_error(self):
        mock_invite = MagicMock()
        mock_invite.used = True
        with patch("modules.auth.services.invite_service.Invite.find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_invite
            from modules.auth.services.invite_service import validate_and_use_invite
            with pytest.raises(AppError) as exc_info:
                await validate_and_use_invite("usedcode")
            assert exc_info.value.status_code == 403
            assert "já utilizado" in exc_info.value.message

    @pytest.mark.asyncio
    async def test_validate_invite_valid_returns_invite(self):
        mock_invite = MagicMock()
        mock_invite.used = False
        mock_invite.role = "ADMIN"
        with patch("modules.auth.services.invite_service.Invite.find_one", new_callable=AsyncMock) as mock_find:
            mock_find.return_value = mock_invite
            from modules.auth.services.invite_service import validate_and_use_invite
            result = await validate_and_use_invite("validcode")
            assert result is mock_invite

    @pytest.mark.asyncio
    async def test_create_invite_returns_code_and_role(self):
        mock_invite = MagicMock()
        mock_invite.insert = AsyncMock()
        with patch("modules.auth.services.invite_service.Invite") as MockInvite:
            MockInvite.return_value = mock_invite
            import modules.auth.services.invite_service as svc
            result = await svc.create_invite(role="ADMIN")
            assert "code" in result
            assert result["role"] == "ADMIN"
            assert len(result["code"]) == 32  # secrets.token_hex(16)
