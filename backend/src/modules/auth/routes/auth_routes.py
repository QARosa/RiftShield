from fastapi import APIRouter, Cookie, Depends, Response

from middleware.dependencies import get_current_user, require_admin
from modules.auth.controllers import auth_controller
from modules.auth.schemas.auth_schema import LoginInput, RegisterInput

router = APIRouter()


@router.post("/register", status_code=201)
async def register(body: RegisterInput, response: Response) -> dict:
    return await auth_controller.register(body, response)


@router.post("/login")
async def login(body: LoginInput, response: Response) -> dict:
    return await auth_controller.login(body, response)


@router.post("/refresh")
async def refresh(response: Response, refresh_token: str | None = Cookie(default=None, alias="refreshToken")) -> dict:
    return await auth_controller.refresh(response, refresh_token)


@router.post("/logout")
async def logout(response: Response, user=Depends(get_current_user)) -> dict:
    return await auth_controller._logout(response, str(user.id))


@router.post("/invite")
async def generate_invite(user=Depends(require_admin)) -> dict:
    return await auth_controller._generate_invite(str(user.id))
