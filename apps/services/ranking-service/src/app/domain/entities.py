from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from .exceptions import RankingInvariantError

DEFAULT_RATING = 1000
ELO_K_FACTOR = 32
DEFAULT_SEASON_DURATION_DAYS = 14
DEFAULT_SEASON_RATING_RESET_PERCENTAGE = 50


class RankingTier(StrEnum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class SeasonStatus(StrEnum):
    ACTIVE = "active"
    FINISHED = "finished"


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


@dataclass(frozen=True)
class LeaderboardEntry:
    position: int
    rating: Rating

    def __post_init__(self) -> None:
        if self.position < 1:
            raise RankingInvariantError("leaderboard position must be positive")


@dataclass(frozen=True)
class SeasonReward:
    player_id: UUID
    position: int
    tier: RankingTier
    planned_credits: int
    planned_badge: str

    def __post_init__(self) -> None:
        if self.position < 1:
            raise RankingInvariantError("season reward position must be positive")

        if self.planned_credits < 0:
            raise RankingInvariantError("season reward credits cannot be negative")

        if not self.planned_badge.strip():
            raise RankingInvariantError("season reward badge is required")

        object.__setattr__(self, "tier", RankingTier(self.tier))
        object.__setattr__(self, "planned_badge", self.planned_badge.strip())


@dataclass(frozen=True)
class Season:
    id: UUID
    name: str
    status: SeasonStatus
    starts_at: datetime
    ends_at: datetime
    rating_reset_percentage: int
    rewards: tuple[SeasonReward, ...] = ()
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_status = SeasonStatus(self.status)
        name = self.name.strip()

        if not name:
            raise RankingInvariantError("season name is required")

        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise RankingInvariantError("season dates must be timezone-aware")

        if self.ends_at <= self.starts_at:
            raise RankingInvariantError("season end must be after start")

        if not 0 <= self.rating_reset_percentage <= 100:
            raise RankingInvariantError("season rating reset must be between 0 and 100")

        if self.finished_at is not None and self.finished_at.tzinfo is None:
            raise RankingInvariantError("season finish date must be timezone-aware")

        if normalized_status == SeasonStatus.ACTIVE and self.finished_at is not None:
            raise RankingInvariantError("active season cannot include finish date")

        if normalized_status == SeasonStatus.FINISHED and self.finished_at is None:
            raise RankingInvariantError("finished season requires finish date")

        object.__setattr__(self, "name", name)
        object.__setattr__(self, "status", normalized_status)

    @property
    def duration_days(self) -> int:
        return (self.ends_at - self.starts_at).days

    def finish(
        self,
        *,
        ratings: tuple[Rating, ...],
        finished_at: datetime | None = None,
    ) -> tuple["Season", tuple[Rating, ...]]:
        if self.status != SeasonStatus.ACTIVE:
            raise RankingInvariantError("only active seasons can be finished")

        checked_at = finished_at or datetime.now(UTC)
        entries = leaderboard_entries(ratings)
        rewards = planned_season_rewards(entries)
        reset_ratings = tuple(
            apply_partial_rating_reset(
                rating,
                reset_percentage=self.rating_reset_percentage,
                updated_at=checked_at,
            )
            for rating in ratings
        )

        return (
            Season(
                id=self.id,
                name=self.name,
                status=SeasonStatus.FINISHED,
                starts_at=self.starts_at,
                ends_at=self.ends_at,
                rating_reset_percentage=self.rating_reset_percentage,
                rewards=rewards,
                finished_at=checked_at,
            ),
            reset_ratings,
        )


def create_season(
    *,
    name: str,
    duration_days: int = DEFAULT_SEASON_DURATION_DAYS,
    rating_reset_percentage: int = DEFAULT_SEASON_RATING_RESET_PERCENTAGE,
    season_id: UUID | None = None,
    starts_at: datetime | None = None,
) -> Season:
    if duration_days < 1:
        raise RankingInvariantError("season duration must be at least one day")

    checked_start = starts_at or datetime.now(UTC)

    return Season(
        id=season_id or uuid4(),
        name=name,
        status=SeasonStatus.ACTIVE,
        starts_at=checked_start,
        ends_at=checked_start + timedelta(days=duration_days),
        rating_reset_percentage=rating_reset_percentage,
    )


def apply_partial_rating_reset(
    rating: Rating,
    *,
    reset_percentage: int,
    updated_at: datetime | None = None,
) -> Rating:
    if not 0 <= reset_percentage <= 100:
        raise RankingInvariantError("season rating reset must be between 0 and 100")

    distance_from_default = rating.score - DEFAULT_RATING
    retained_percentage = 100 - reset_percentage
    reset_score = DEFAULT_RATING + round(
        distance_from_default * retained_percentage / 100
    )

    return Rating(
        player_id=rating.player_id,
        score=max(0, reset_score),
        wins=0,
        losses=0,
        applied_match_ids=(),
        updated_at=updated_at or datetime.now(UTC),
    )


def planned_season_rewards(
    entries: tuple[LeaderboardEntry, ...],
) -> tuple[SeasonReward, ...]:
    rewards: list[SeasonReward] = []
    reward_plan = (
        (1, 10, "season_champion"),
        (2, 5, "season_runner_up"),
        (3, 3, "season_top_three"),
    )
    credits_by_position = {
        position: (planned_credits, planned_badge)
        for position, planned_credits, planned_badge in reward_plan
    }

    for entry in entries:
        reward = credits_by_position.get(entry.position)

        if reward is None:
            continue

        planned_credits, planned_badge = reward
        rewards.append(
            SeasonReward(
                player_id=entry.rating.player_id,
                position=entry.position,
                tier=entry.rating.tier,
                planned_credits=planned_credits,
                planned_badge=planned_badge,
            )
        )

    return tuple(rewards)


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


def leaderboard_entries(
    ratings: tuple[Rating, ...],
    *,
    offset: int = 0,
    limit: int | None = None,
) -> tuple[LeaderboardEntry, ...]:
    if offset < 0:
        raise RankingInvariantError("leaderboard offset cannot be negative")

    if limit is not None and limit < 1:
        raise RankingInvariantError("leaderboard limit must be positive")

    ordered_ratings = sorted(
        ratings,
        key=lambda rating: (
            -rating.score,
            -rating.wins,
            rating.losses,
            str(rating.player_id),
        ),
    )
    window = ordered_ratings[offset : offset + limit if limit is not None else None]

    return tuple(
        LeaderboardEntry(position=offset + index + 1, rating=rating)
        for index, rating in enumerate(window)
    )
