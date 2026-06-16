from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from .exceptions import RankingInvariantError

DEFAULT_RATING = 1000
ELO_K_FACTOR = 32


class RankingTier(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


@dataclass(frozen=True)
class Rating:
    player_id: UUID
    score: int
    wins: int = 0
    losses: int = 0
    applied_match_ids: tuple[UUID, ...] = ()
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.score < 0:
            raise RankingInvariantError("rating score cannot be negative")

        if self.wins < 0 or self.losses < 0:
            raise RankingInvariantError("rating results cannot be negative")

        if len(self.applied_match_ids) != len(set(self.applied_match_ids)):
            raise RankingInvariantError("rating cannot contain duplicated matches")

    @property
    def tier(self) -> RankingTier:
        return tier_for_score(self.score)

    @property
    def matches_played(self) -> int:
        return self.wins + self.losses

    def has_applied_match(self, match_id: UUID) -> bool:
        return match_id in self.applied_match_ids

    def with_match_result(
        self,
        *,
        match_id: UUID,
        new_score: int,
        won: bool,
        updated_at: datetime | None = None,
    ) -> "Rating":
        if self.has_applied_match(match_id):
            return self

        normalized_score = max(0, new_score)

        return Rating(
            player_id=self.player_id,
            score=normalized_score,
            wins=self.wins + (1 if won else 0),
            losses=self.losses + (0 if won else 1),
            applied_match_ids=(*self.applied_match_ids, match_id),
            updated_at=updated_at or datetime.now(UTC),
        )


def create_rating(player_id: UUID) -> Rating:
    return Rating(player_id=player_id, score=DEFAULT_RATING)


def tier_for_score(score: int) -> RankingTier:
    if score < 0:
        raise RankingInvariantError("rating score cannot be negative")

    if score < 1000:
        return RankingTier.BRONZE

    if score < 1500:
        return RankingTier.SILVER

    if score < 2000:
        return RankingTier.GOLD

    if score < 2500:
        return RankingTier.PLATINUM

    return RankingTier.DIAMOND


def recalculate_elo_ratings(
    *,
    winner: Rating,
    loser: Rating,
    match_id: UUID,
    updated_at: datetime | None = None,
) -> tuple[Rating, Rating, bool]:
    if winner.player_id == loser.player_id:
        raise RankingInvariantError("winner and loser must be different players")

    if winner.has_applied_match(match_id) and loser.has_applied_match(match_id):
        return winner, loser, False

    if winner.has_applied_match(match_id) or loser.has_applied_match(match_id):
        raise RankingInvariantError("match rating application is inconsistent")

    checked_at = updated_at or datetime.now(UTC)
    winner_expected = expected_score(winner.score, loser.score)
    loser_expected = expected_score(loser.score, winner.score)

    winner_score = round(winner.score + ELO_K_FACTOR * (1 - winner_expected))
    loser_score = round(loser.score + ELO_K_FACTOR * (0 - loser_expected))

    return (
        winner.with_match_result(
            match_id=match_id,
            new_score=winner_score,
            won=True,
            updated_at=checked_at,
        ),
        loser.with_match_result(
            match_id=match_id,
            new_score=loser_score,
            won=False,
            updated_at=checked_at,
        ),
        True,
    )


def expected_score(player_score: int, opponent_score: int) -> float:
    return 1 / (1 + 10 ** ((opponent_score - player_score) / 400))
