from fastapi import Cookie, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional

from shared.utils.errors import ForbiddenError, UnauthorizedError
from shared.utils.token import verify_access_token, verify_refresh_token, generate_access_token


security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    access_token: Optional[str] = Cookie(default=None, alias="accessToken"),
    refresh_token: Optional[str] = Cookie(default=None, alias="refreshToken"),
):
    from modules.auth.models.user_model import User

    token = access_token
    if credentials:
        token = credentials.credentials

    if not token:
        raise UnauthorizedError("Token não fornecido")

    try:
        payload = verify_access_token(token)
        user = await User.get(payload["userId"])
        if user:
            return user
    except Exception:
        pass

    if refresh_token:
        try:
            payload = verify_refresh_token(refresh_token)
            user = await User.get(payload["userId"])
            if user:
                new_access = generate_access_token(str(user.id), user.email)
                request.state.new_access_token = new_access
                return user
        except Exception:
            pass

    raise UnauthorizedError("Token inválido ou expirado")


async def require_admin(user=Depends(get_current_user)):
    if getattr(user, "role", "").upper() != "ADMIN":
        raise ForbiddenError()
    return user
