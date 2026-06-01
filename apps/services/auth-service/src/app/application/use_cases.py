from dataclasses import dataclass

from app.domain.entities import AuthSession, Player, grant_initial_onboarding
from app.domain.exceptions import (
    InvalidCredentialsError,
    PlayerAlreadyExistsError,
    PlayerNotFoundError,
)
from app.domain.repositories import PlayerRepository

from .security import (
    JWT_TTL_SECONDS,
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)


@dataclass(frozen=True)
class RegisterPlayerCommand:
    nickname: str
    email: str
    password: str


@dataclass(frozen=True)
class LoginPlayerCommand:
    email: str
    password: str


@dataclass(frozen=True)
class GetCurrentPlayerProfileQuery:
    access_token: str


@dataclass(frozen=True)
class AuthResult:
    player: Player
    session: AuthSession


class RegisterPlayer:
    def __init__(self, repository: PlayerRepository) -> None:
        self.repository = repository

    def execute(self, command: RegisterPlayerCommand) -> AuthResult:
        email = command.email.strip().lower()
        nickname = command.nickname.strip()

        if self.repository.find_by_email(email) or self.repository.find_by_nickname(nickname):
            raise PlayerAlreadyExistsError("player already exists")

        player = grant_initial_onboarding(
            Player(
                nickname=nickname,
                email=email,
                password_hash=hash_password(command.password),
            )
        )
        self.repository.add(player)

        return AuthResult(player=player, session=create_session(player))


class LoginPlayer:
    def __init__(self, repository: PlayerRepository) -> None:
        self.repository = repository

    def execute(self, command: LoginPlayerCommand) -> AuthResult:
        email = command.email.strip().lower()
        player = self.repository.find_by_email(email)

        if player is None or not verify_password(command.password, player.password_hash):
            raise InvalidCredentialsError("invalid credentials")

        return AuthResult(player=player, session=create_session(player))


class GetCurrentPlayerProfile:
    def __init__(self, repository: PlayerRepository) -> None:
        self.repository = repository

    def execute(self, query: GetCurrentPlayerProfileQuery) -> Player:
        player_id = verify_access_token(query.access_token)
        player = self.repository.find_by_id(player_id)

        if player is None:
            raise PlayerNotFoundError("player not found")

        player_with_onboarding = grant_initial_onboarding(player)

        if player_with_onboarding != player:
            self.repository.save(player_with_onboarding)

        return player_with_onboarding


def create_session(player: Player) -> AuthSession:
    return AuthSession(
        player_id=player.id,
        access_token=create_access_token(player_id=player.id),
        token_type="bearer",
        expires_in=JWT_TTL_SECONDS,
    )
