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
from app.domain.entities import CreditLedgerEntry, InitialDeckCard, OnboardingRewards, Player
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


class InitialDeckCardResponse(BaseModel):
    id: str
    name: str
    level: int
    expires_at: datetime
    family: str
    rarity_label: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int


class CreditLedgerEntryResponse(BaseModel):
    id: str
    amount: int
    reason: str
    created_at: datetime


class OnboardingRewardsResponse(BaseModel):
    initial_deck: list[InitialDeckCardResponse]
    initial_credits: int
    credit_ledger: list[CreditLedgerEntryResponse]
    granted_at: datetime


class PlayerProfileResponse(PlayerResponse):
    created_at: datetime
    social_login: SocialLoginMetadataResponse
    onboarding: OnboardingRewardsResponse


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    player: PlayerResponse
    onboarding: OnboardingRewardsResponse


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
        onboarding=onboarding_response(result.player.onboarding),
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
        onboarding=onboarding_response(player.onboarding),
    )


def onboarding_response(rewards: OnboardingRewards | None) -> OnboardingRewardsResponse:
    if rewards is None:
        raise RuntimeError("player onboarding must be granted before serializing response")

    return OnboardingRewardsResponse(
        initial_deck=[initial_deck_card_response(card) for card in rewards.initial_deck],
        initial_credits=rewards.initial_credits,
        credit_ledger=[credit_ledger_entry_response(entry) for entry in rewards.credit_ledger],
        granted_at=rewards.granted_at,
    )


def initial_deck_card_response(card: InitialDeckCard) -> InitialDeckCardResponse:
    return InitialDeckCardResponse(
        id=str(card.id),
        name=card.name,
        family=card.family,
        rarity_label=card.rarity_label,
        speed=card.speed,
        strength=card.strength,
        intelligence=card.intelligence,
        resistance=card.resistance,
        rarity=card.rarity,
        level=card.level,
        expires_at=card.expires_at,
    )


def credit_ledger_entry_response(entry: CreditLedgerEntry) -> CreditLedgerEntryResponse:
    return CreditLedgerEntryResponse(
        id=str(entry.id),
        amount=entry.amount,
        reason=entry.reason,
        created_at=entry.created_at,
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
