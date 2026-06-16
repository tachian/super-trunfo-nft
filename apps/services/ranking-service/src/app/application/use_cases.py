from dataclasses import dataclass
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import (
    LeaderboardEntry,
    Rating,
    create_rating,
    leaderboard_entries,
    recalculate_elo_ratings,
)
from app.domain.events import player_rank_updated_event
from app.domain.repositories import DomainEventPublisher, LeaderboardCache, RatingRepository


@dataclass(frozen=True)
class RecalculatePlayerRatingCommand:
    match_id: UUID
    winner_id: UUID
    loser_id: UUID


@dataclass(frozen=True)
class RecalculatePlayerRatingResult:
    winner_rating: Rating
    loser_rating: Rating
    created: bool
    events: tuple[DomainEvent, ...]


@dataclass(frozen=True)
class GetGlobalRankingQuery:
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class GetFriendsRankingQuery:
    player_id: UUID
    friend_ids: tuple[UUID, ...] = ()
    limit: int = 50
    offset: int = 0


@dataclass(frozen=True)
class RankingQueryResult:
    entries: tuple[LeaderboardEntry, ...]
    total: int
    limit: int
    offset: int
    cache_key: str
    cache_hit: bool


class RecalculatePlayerRating:
    def __init__(
        self,
        rating_repository: RatingRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.rating_repository = rating_repository
        self.event_publisher = event_publisher

    def execute(
        self,
        command: RecalculatePlayerRatingCommand,
    ) -> RecalculatePlayerRatingResult:
        winner = self.rating_repository.find_by_player_id(
            command.winner_id
        ) or create_rating(command.winner_id)
        loser = self.rating_repository.find_by_player_id(
            command.loser_id
        ) or create_rating(command.loser_id)
        previous_winner_score = winner.score
        previous_loser_score = loser.score

        updated_winner, updated_loser, created = recalculate_elo_ratings(
            winner=winner,
            loser=loser,
            match_id=command.match_id,
        )

        if not created:
            return RecalculatePlayerRatingResult(
                winner_rating=updated_winner,
                loser_rating=updated_loser,
                created=False,
                events=(),
            )

        self.rating_repository.save_many((updated_winner, updated_loser))
        events = (
            player_rank_updated_event(
                match_id=str(command.match_id),
                rating=updated_winner,
                previous_score=previous_winner_score,
            ),
            player_rank_updated_event(
                match_id=str(command.match_id),
                rating=updated_loser,
                previous_score=previous_loser_score,
            ),
        )

        for event in events:
            self.event_publisher.publish(event)

        return RecalculatePlayerRatingResult(
            winner_rating=updated_winner,
            loser_rating=updated_loser,
            created=True,
            events=events,
        )


class GetGlobalRanking:
    def __init__(
        self,
        rating_repository: RatingRepository,
        leaderboard_cache: LeaderboardCache,
    ) -> None:
        self.rating_repository = rating_repository
        self.leaderboard_cache = leaderboard_cache

    def execute(self, query: GetGlobalRankingQuery) -> RankingQueryResult:
        ratings = self.rating_repository.list_all()
        cache_key = ranking_cache_key(
            "global",
            repository_version=self.rating_repository.version(),
            limit=query.limit,
            offset=query.offset,
        )

        return cached_leaderboard_result(
            cache=self.leaderboard_cache,
            ratings=ratings,
            cache_key=cache_key,
            limit=query.limit,
            offset=query.offset,
        )


class GetFriendsRanking:
    def __init__(
        self,
        rating_repository: RatingRepository,
        leaderboard_cache: LeaderboardCache,
    ) -> None:
        self.rating_repository = rating_repository
        self.leaderboard_cache = leaderboard_cache

    def execute(self, query: GetFriendsRankingQuery) -> RankingQueryResult:
        friend_id_set = set(query.friend_ids)
        ratings = tuple(
            rating
            for rating in self.rating_repository.list_all()
            if rating.player_id in friend_id_set
        )
        cache_key = ranking_cache_key(
            "friends",
            repository_version=self.rating_repository.version(),
            limit=query.limit,
            offset=query.offset,
            player_id=query.player_id,
            friend_ids=tuple(sorted(friend_id_set)),
        )

        return cached_leaderboard_result(
            cache=self.leaderboard_cache,
            ratings=ratings,
            cache_key=cache_key,
            limit=query.limit,
            offset=query.offset,
        )


def cached_leaderboard_result(
    *,
    cache: LeaderboardCache,
    ratings: tuple[Rating, ...],
    cache_key: str,
    limit: int,
    offset: int,
) -> RankingQueryResult:
    cached_entries = cache.get(cache_key)

    if cached_entries is not None:
        return RankingQueryResult(
            entries=cached_entries,
            total=len(ratings),
            limit=limit,
            offset=offset,
            cache_key=cache_key,
            cache_hit=True,
        )

    entries = leaderboard_entries(ratings, limit=limit, offset=offset)
    cache.set(cache_key, entries)

    return RankingQueryResult(
        entries=entries,
        total=len(ratings),
        limit=limit,
        offset=offset,
        cache_key=cache_key,
        cache_hit=False,
    )


def ranking_cache_key(
    scope: str,
    *,
    repository_version: int,
    limit: int,
    offset: int,
    player_id: UUID | None = None,
    friend_ids: tuple[UUID, ...] = (),
) -> str:
    friend_ids_key = ",".join(str(friend_id) for friend_id in friend_ids)
    player_id_key = str(player_id) if player_id is not None else ""

    return (
        f"{scope}:v{repository_version}:limit:{limit}:offset:{offset}:"
        f"player:{player_id_key}:friends:{friend_ids_key}"
    )
