import re
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Header, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.application.use_cases import (
    AuthResult,
    GetCurrentPlayerProfile,
    GetCurrentPlayerProfileQuery,
    LoginPlayer,
    LoginPlayerCommand,
    RegisterPlayer,
    RegisterPlayerCommand,
)
from app.domain.entities import Player
from app.domain.exceptions import (
    InvalidAccessTokenError,
    InvalidCredentialsError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterPlayerRequest(BaseModel):
    nickname: Annotated[str, Field(min_length=3, max_length=50)]
    email: Annotated[str, Field(min_length=5, max_length=254)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()

        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("invalid email format")

        return normalized

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("nickname cannot be blank")

        return normalized


class LoginPlayerRequest(BaseModel):
    email: Annotated[str, Field(min_length=5, max_length=254)]
    password: Annotated[str, Field(min_length=8, max_length=128)]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()

        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("invalid email format")

        return normalized


class PlayerResponse(BaseModel):
    id: str
    nickname: str
    rating: int
    credits: int


class SocialLoginMetadataResponse(BaseModel):
    provider: str
    subject: str | None = None


class PlayerProfileResponse(PlayerResponse):
    created_at: datetime
    social_login: SocialLoginMetadataResponse


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    player: PlayerResponse


def create_identity_router() -> APIRouter:
    router = APIRouter(tags=["identity"])

    @router.post(
        "/auth/register",
        status_code=status.HTTP_201_CREATED,
        response_model=AuthResponse,
        responses={409: {"description": "Email or nickname already registered"}},
    )
    async def register_player(payload: RegisterPlayerRequest, request: Request) -> AuthResponse:
        use_case = RegisterPlayer(request.app.state.player_repository)

        try:
            result = use_case.execute(
                RegisterPlayerCommand(
                    nickname=payload.nickname,
                    email=payload.email,
                    password=payload.password,
                )
            )
        except PlayerAlreadyExistsError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Player already exists."},
            )

        return auth_response(result)

    @router.post(
        "/auth/login",
        response_model=AuthResponse,
        responses={401: {"description": "Invalid credentials"}},
    )
    async def login_player(payload: LoginPlayerRequest, request: Request) -> AuthResponse:
        use_case = LoginPlayer(request.app.state.player_repository)

        try:
            result = use_case.execute(
                LoginPlayerCommand(email=payload.email, password=payload.password)
            )
        except InvalidCredentialsError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid credentials."},
            )

        return auth_response(result)

    @router.get(
        "/players/me",
        response_model=PlayerProfileResponse,
        responses={401: {"description": "Invalid or missing bearer token"}},
    )
    async def current_player_profile(
        request: Request,
        authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    ) -> PlayerProfileResponse | JSONResponse:
        access_token = extract_bearer_token(authorization)

        if access_token is None:
            return authentication_error()

        use_case = GetCurrentPlayerProfile(request.app.state.player_repository)

        try:
            player = use_case.execute(GetCurrentPlayerProfileQuery(access_token=access_token))
        except (InvalidAccessTokenError, PlayerNotFoundError):
            return authentication_error()

        return player_profile_response(player)

    return router


def auth_response(result: AuthResult) -> AuthResponse:
    return AuthResponse(
        access_token=result.session.access_token,
        token_type=result.session.token_type,
        expires_in=result.session.expires_in,
        player=PlayerResponse(
            id=str(result.player.id),
            nickname=result.player.nickname,
            rating=result.player.rating,
            credits=result.player.credits,
        ),
    )


def player_profile_response(player: Player) -> PlayerProfileResponse:
    return PlayerProfileResponse(
        id=str(player.id),
        nickname=player.nickname,
        rating=player.rating,
        credits=player.credits,
        created_at=player.created_at,
        social_login=SocialLoginMetadataResponse(
            provider=player.social_login_provider,
            subject=player.social_login_subject,
        ),
    )


def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token.strip():
        return None

    return token.strip()


def authentication_error() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid or missing bearer token."},
    )
