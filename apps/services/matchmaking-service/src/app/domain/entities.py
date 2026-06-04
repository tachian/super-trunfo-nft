from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from .exceptions import MatchmakingInvariantError

LEVEL_TOLERANCE = 20
BRONZE_MAX_LEVEL = 999
SILVER_MAX_LEVEL = 1499


class MatchmakingTier(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


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
