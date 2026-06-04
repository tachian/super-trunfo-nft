from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .exceptions import MatchmakingInvariantError

LEVEL_TOLERANCE = 20
BRONZE_MAX_LEVEL = 999
SILVER_MAX_LEVEL = 1499


class MatchmakingTier(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


class MatchmakingMode(StrEnum):
    PVP = "pvp"
    PVE = "pve"


class MatchmakingOpponentKind(StrEnum):
    PLAYER = "player"
    BOT = "bot"


@dataclass(frozen=True)
class TierQueue:
    tier: MatchmakingTier
    name: str

    def __post_init__(self) -> None:
        normalized_tier = MatchmakingTier(self.tier)
        expected_name = queue_name_for_tier(normalized_tier)

        if self.name != expected_name:
            raise MatchmakingInvariantError("tier queue name does not match tier")

        object.__setattr__(self, "tier", normalized_tier)


@dataclass(frozen=True)
class MatchmakingTicket:
    id: UUID
    player_id: UUID
    average_deck_level: int
    tier: MatchmakingTier

    def __post_init__(self) -> None:
        if self.average_deck_level < 0:
            raise MatchmakingInvariantError("average deck level cannot be negative")

        expected_tier = tier_for_average_level(self.average_deck_level)
        normalized_tier = MatchmakingTier(self.tier)

        if normalized_tier != expected_tier:
            raise MatchmakingInvariantError("matchmaking ticket tier does not match deck level")

        object.__setattr__(self, "tier", normalized_tier)

    def is_compatible_with(
        self,
        other: "MatchmakingTicket",
        tolerance: int = LEVEL_TOLERANCE,
    ) -> bool:
        if self.player_id == other.player_id:
            return False

        if self.tier != other.tier:
            return False

        return abs(self.average_deck_level - other.average_deck_level) <= tolerance


@dataclass(frozen=True)
class MatchmakingOpponent:
    id: UUID
    kind: MatchmakingOpponentKind
    average_deck_level: int
    tier: MatchmakingTier
    ticket_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.average_deck_level < 0:
            raise MatchmakingInvariantError("opponent average deck level cannot be negative")

        normalized_kind = MatchmakingOpponentKind(self.kind)
        expected_tier = tier_for_average_level(self.average_deck_level)
        normalized_tier = MatchmakingTier(self.tier)

        if normalized_tier != expected_tier:
            raise MatchmakingInvariantError("opponent tier does not match deck level")

        if normalized_kind == MatchmakingOpponentKind.PLAYER and self.ticket_id is None:
            raise MatchmakingInvariantError("player opponent must reference a ticket")

        if normalized_kind == MatchmakingOpponentKind.BOT and self.ticket_id is not None:
            raise MatchmakingInvariantError("bot opponent cannot reference a player ticket")

        object.__setattr__(self, "kind", normalized_kind)
        object.__setattr__(self, "tier", normalized_tier)


@dataclass(frozen=True)
class MatchmakingMatch:
    id: UUID
    mode: MatchmakingMode
    player_ticket: MatchmakingTicket
    opponent: MatchmakingOpponent

    def __post_init__(self) -> None:
        normalized_mode = MatchmakingMode(self.mode)

        if self.player_ticket.player_id == self.opponent.id:
            raise MatchmakingInvariantError("matchmaking participants must be different")

        if self.player_ticket.tier != self.opponent.tier:
            raise MatchmakingInvariantError(
                "matchmaking match must keep opponents in the same tier"
            )

        if normalized_mode == MatchmakingMode.PVE:
            if self.opponent.kind != MatchmakingOpponentKind.BOT:
                raise MatchmakingInvariantError("pve match must use a bot opponent")
            if self.player_ticket.average_deck_level != self.opponent.average_deck_level:
                raise MatchmakingInvariantError("bot fallback must use an equivalent deck level")

        if (
            normalized_mode == MatchmakingMode.PVP
            and self.opponent.kind != MatchmakingOpponentKind.PLAYER
        ):
            raise MatchmakingInvariantError("pvp match must use a player opponent")

        object.__setattr__(self, "mode", normalized_mode)


@dataclass(frozen=True)
class MatchStartedEvent:
    match_id: UUID
    mode: MatchmakingMode
    player_id: UUID
    opponent_id: UUID
    opponent_kind: MatchmakingOpponentKind
    player_average_deck_level: int
    opponent_average_deck_level: int
    occurred_at: datetime
    name: str = "MatchStarted"
    schema_version: str = "1.0.0"

    def __post_init__(self) -> None:
        object.__setattr__(self, "mode", MatchmakingMode(self.mode))
        object.__setattr__(
            self,
            "opponent_kind",
            MatchmakingOpponentKind(self.opponent_kind),
        )


def create_pvp_match(
    *,
    ticket: MatchmakingTicket,
    opponent_ticket: MatchmakingTicket,
    match_id: UUID | None = None,
) -> MatchmakingMatch:
    return MatchmakingMatch(
        id=match_id or uuid4(),
        mode=MatchmakingMode.PVP,
        player_ticket=ticket,
        opponent=MatchmakingOpponent(
            id=opponent_ticket.player_id,
            kind=MatchmakingOpponentKind.PLAYER,
            average_deck_level=opponent_ticket.average_deck_level,
            tier=opponent_ticket.tier,
            ticket_id=opponent_ticket.id,
        ),
    )


def create_pve_match(
    *,
    ticket: MatchmakingTicket,
    match_id: UUID | None = None,
    bot_id: UUID | None = None,
) -> MatchmakingMatch:
    return MatchmakingMatch(
        id=match_id or uuid4(),
        mode=MatchmakingMode.PVE,
        player_ticket=ticket,
        opponent=MatchmakingOpponent(
            id=bot_id or uuid4(),
            kind=MatchmakingOpponentKind.BOT,
            average_deck_level=ticket.average_deck_level,
            tier=ticket.tier,
        ),
    )


def match_started_event(
    match: MatchmakingMatch,
    occurred_at: datetime | None = None,
) -> MatchStartedEvent:
    return MatchStartedEvent(
        match_id=match.id,
        mode=match.mode,
        player_id=match.player_ticket.player_id,
        opponent_id=match.opponent.id,
        opponent_kind=match.opponent.kind,
        player_average_deck_level=match.player_ticket.average_deck_level,
        opponent_average_deck_level=match.opponent.average_deck_level,
        occurred_at=occurred_at or datetime.now(UTC),
    )


def queue_name_for_tier(tier: MatchmakingTier) -> str:
    return f"queue:{tier.value}"


def tier_for_average_level(average_deck_level: int) -> MatchmakingTier:
    if average_deck_level < 0:
        raise MatchmakingInvariantError("average deck level cannot be negative")

    if average_deck_level <= BRONZE_MAX_LEVEL:
        return MatchmakingTier.BRONZE

    if average_deck_level <= SILVER_MAX_LEVEL:
        return MatchmakingTier.SILVER

    return MatchmakingTier.GOLD


def configured_tier_queues() -> tuple[TierQueue, ...]:
    return tuple(
        TierQueue(tier=tier, name=queue_name_for_tier(tier))
        for tier in MatchmakingTier
    )
