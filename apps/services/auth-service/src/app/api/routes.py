import re
from typing import Annotated

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.application.use_cases import (
    AuthResult,
    LoginPlayer,
    LoginPlayerCommand,
    RegisterPlayer,
    RegisterPlayerCommand,
)
from app.domain.exceptions import InvalidCredentialsError, PlayerAlreadyExistsError

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

    @router.get("/players/me", status_code=status.HTTP_202_ACCEPTED)
    async def current_player_profile() -> dict[str, str]:
        return {"service": "auth-service", "status": "planned", "task": "ST-102"}

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
