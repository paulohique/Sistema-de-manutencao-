from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import create_access_token, get_current_user, ldap_authenticate
from app.schemas.schemas import LoginRequest, LoginResponse, UserOut


router = APIRouter(tags=["auth"])


@router.post("/api/auth/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    info = ldap_authenticate(payload.username, payload.password)
    token = create_access_token(
        {
            "sub": info.get("username"),
            "display_name": info.get("display_name"),
            "email": info.get("email"),
            "groups": info.get("groups", []),
        }
    )
    user = UserOut(
        username=str(info.get("username")),
        display_name=info.get("display_name"),
        email=info.get("email"),
        groups=list(info.get("groups") or []),
    )
    return LoginResponse(access_token=token, user=user)


@router.get("/api/auth/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return UserOut(
        username=str(user.get("sub")),
        display_name=user.get("display_name"),
        email=user.get("email"),
        groups=list(user.get("groups") or []),
    )
