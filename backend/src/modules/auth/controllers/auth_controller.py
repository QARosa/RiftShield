from __future__ import annotations

from fastapi import Depends, Response

from config.settings import get_settings
from modules.auth.schemas.auth_schema import LoginInput, RegisterInput
from modules.auth.services import auth_service
from modules.auth.services.invite_service import create_invite


def _current_user():
    from middleware.auth import get_current_user
    return Depends(get_current_user)


settings = get_settings()


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="accessToken",
        value=access_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=15 * 60,
    )
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/auth",
    )


async def register(data: RegisterInput, response: Response) -> dict:
    result = await auth_service.register_user(data)
    _set_auth_cookies(response, result["accessToken"], result["refreshToken"])
    payload = {"user": result["user"].model_dump()}
    # Expose tokens outside production so E2E (Cypress) can cy.setCookie reliably
    if not settings.is_production:
        payload["accessToken"] = result["accessToken"]
        payload["refreshToken"] = result["refreshToken"]
    return payload


async def login(data: LoginInput, response: Response) -> dict:
    result = await auth_service.login_user(data)
    _set_auth_cookies(response, result["accessToken"], result["refreshToken"])
    payload = {"user": result["user"].model_dump()}
    if not settings.is_production:
        payload["accessToken"] = result["accessToken"]
        payload["refreshToken"] = result["refreshToken"]
    return payload


async def refresh(response: Response, refresh_token: str | None = None) -> dict:
    if not refresh_token:
        from fastapi.exceptions import HTTPException
        raise HTTPException(status_code=401, detail="Refresh token n\u00e3o fornecido")

    result = await auth_service.refresh_tokens(refresh_token)
    _set_auth_cookies(response, result["accessToken"], result["refreshToken"])
    return {"message": "Tokens renovados"}


async def _logout(response: Response, user_id: str) -> dict:
    await auth_service.logout_user(user_id)
    response.delete_cookie("accessToken")
    response.delete_cookie("refreshToken", path="/api/auth")
    return {"message": "Logout realizado com sucesso"}


async def _get_profile(user_id: str) -> dict:
    profile = await auth_service.get_profile(user_id)
    return {"user": profile.model_dump()}


async def _update_profile(user_id: str, data: dict) -> dict:
    profile = await auth_service.update_profile(user_id, data)
    return {"user": profile.model_dump()}


async def _generate_invite(user_id: str) -> dict:
    result = await create_invite()
    return {"invite": result}
