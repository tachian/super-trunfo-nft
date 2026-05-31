from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Player:
    nickname: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    rating: int = 1000
    credits: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class AuthSession:
    player_id: UUID
    access_token: str
    token_type: str
    expires_in: int
