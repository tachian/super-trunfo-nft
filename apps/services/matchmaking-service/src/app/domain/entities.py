from dataclasses import dataclass
from enum import StrEnum

from .exceptions import MatchmakingInvariantError


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


def queue_name_for_tier(tier: MatchmakingTier) -> str:
    return f"queue:{tier.value}"


def configured_tier_queues() -> tuple[TierQueue, ...]:
    return tuple(
        TierQueue(tier=tier, name=queue_name_for_tier(tier))
        for tier in MatchmakingTier
    )
