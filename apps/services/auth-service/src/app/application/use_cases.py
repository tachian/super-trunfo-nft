from dataclasses import dataclass

from app.domain.entities import AuthSession, Player
from app.domain.exceptions import InvalidCredentialsError, PlayerAlreadyExistsError
from app.domain.repositories import PlayerRepository

from .security import JWT_TTL_SECONDS, create_access_token, hash_password, verify_password


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

        player = Player(
            nickname=nickname,
            email=email,
            password_hash=hash_password(command.password),
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


def create_session(player: Player) -> AuthSession:
    return AuthSession(
        player_id=player.id,
        access_token=create_access_token(player_id=player.id),
        token_type="bearer",
        expires_in=JWT_TTL_SECONDS,
    )
