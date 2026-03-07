import secrets
import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, Cookie, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.password import hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    DiscordAuthUrlResponse,
    DiscordCallbackRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordConfirm,
    ResetPasswordRequest,
    TokenResponse,
)
from app.services.email import send_password_reset_email, send_welcome_email
from app.utils.cache import discord_oauth_states

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or user.password is None or not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id, user.get_roles_list())
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, response: Response, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Check uniqueness
    existing = await db.execute(select(User).where((User.email == data.email) | (User.nickname == data.nickname)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or nickname already exists")

    user = User(
        email=data.email,
        password=hash_password(data.password),
        nickname=data.nickname,
        roles="ROLE_USER",
        sim_dcs=True,
        status=User.STATUS_UNKNOWN,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    background_tasks.add_task(send_welcome_email, user.email, user.nickname)

    access_token = create_access_token(user.id, user.get_roles_list())
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(response: Response, refresh_token: str | None = Cookie(default=None), db: AsyncSession = Depends(get_db)):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = int(payload["sub"])
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = create_access_token(user.id, user.get_roles_list())
    new_refresh = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(access_token=new_access)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"detail": "Logged out"}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None:
        # Don't reveal if email exists
        return {"detail": "If this email exists, a reset link has been sent."}

    token = str(uuid.uuid4())
    user.password_request_token = token
    user.password_request_expired_at = datetime.now(UTC) + timedelta(hours=24)
    await db.commit()

    background_tasks.add_task(send_password_reset_email, user.email, user.nickname or user.email, token)
    return {"detail": "If this email exists, a reset link has been sent."}


@router.post("/reset-password/confirm")
async def reset_password_confirm(data: ResetPasswordConfirm, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.password_request_token == data.token))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    if user.password_request_expired_at and user.password_request_expired_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")

    user.password = hash_password(data.password)
    user.password_request_token = None
    user.password_request_expired_at = None
    user.updated_at = datetime.now(UTC)
    await db.commit()

    return {"detail": "Password updated"}


# --- Discord OAuth2 ---

DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"


@router.get("/discord/authorize", response_model=DiscordAuthUrlResponse)
async def discord_authorize():
    if not settings.DISCORD_CLIENT_ID:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Discord SSO is not configured")

    state = secrets.token_urlsafe(32)
    discord_oauth_states[state] = True

    params = urlencode({
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify email",
        "state": state,
    })

    return DiscordAuthUrlResponse(authorization_url=f"{DISCORD_AUTHORIZE_URL}?{params}")


@router.post("/discord/callback", response_model=TokenResponse)
async def discord_callback(data: DiscordCallbackRequest, response: Response, db: AsyncSession = Depends(get_db)):
    # Validate state (CSRF protection) — check first to reject forged requests early
    if data.state not in discord_oauth_states:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired state parameter")
    del discord_oauth_states[data.state]

    # Validate Discord OAuth configuration before attempting token exchange
    if (
        not settings.DISCORD_CLIENT_ID
        or not settings.DISCORD_CLIENT_SECRET.get_secret_value()
        or not settings.DISCORD_REDIRECT_URI
    ):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Discord SSO is not configured",
        )

    # Exchange code for Discord access token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET.get_secret_value(),
                "grant_type": "authorization_code",
                "code": data.code,
                "redirect_uri": settings.DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    if token_resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange Discord authorization code")

    discord_access_token = token_resp.json()["access_token"]

    # Fetch Discord user info
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(
            DISCORD_USER_URL,
            headers={"Authorization": f"Bearer {discord_access_token}"},
        )

    if user_resp.status_code != 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch Discord user info")

    discord_user = user_resp.json()
    discord_id = discord_user["id"]
    discord_username = discord_user.get("global_name") or discord_user["username"]
    discord_email = discord_user.get("email")
    email_verified = discord_user.get("verified", False)

    if not discord_email or not email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Votre email Discord n'est pas vérifié. Veuillez vérifier votre email Discord avant de vous connecter.",
        )

    # Find or create user
    # 1. Try by discord_id
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()

    if user is None:
        # 2. Try by email
        result = await db.execute(select(User).where(User.email == discord_email))
        user = result.scalar_one_or_none()

        if user is not None:
            # Link discord_id to existing account
            user.discord_id = discord_id
            user.discord = discord_username
            user.updated_at = datetime.now(UTC)
        else:
            # 3. Create new user
            nickname = discord_username
            for _ in range(5):
                existing = await db.execute(select(User).where(User.nickname == nickname))
                if existing.scalar_one_or_none() is None:
                    break
                nickname = f"{discord_username}_{secrets.randbelow(10000):04d}"

            user = User(
                email=discord_email,
                password=None,
                nickname=nickname,
                discord_id=discord_id,
                discord=discord_username,
                roles="ROLE_USER",
                status=User.STATUS_UNKNOWN,
                sim_dcs=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            db.add(user)
    else:
        # Update discord username if changed
        if user.discord != discord_username:
            user.discord = discord_username
            user.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(user)

    # Issue JWT tokens
    access_token = create_access_token(user.id, user.get_roles_list())
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)
