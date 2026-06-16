from datetime import UTC, datetime
from uuid import UUID

from app.application.use_cases import (
    GetFriendsRanking,
    GetFriendsRankingQuery,
    GetGlobalRanking,
    GetGlobalRankingQuery,
    RecalculatePlayerRating,
    RecalculatePlayerRatingCommand,
)
from app.domain.entities import Rating
from app.infrastructure.repositories import InMemoryLeaderboardCache, InMemoryRatingRepository
from super_trunfo_shared import InMemoryDomainEventPublisher

WINNER_ID = UUID("11111111-1111-4111-8111-000000000503")
LOSER_ID = UUID("22222222-2222-4222-8222-000000000503")
MATCH_ID = UUID("33333333-3333-4333-8333-000000000503")


def test_recalculate_player_rating_persists_ratings_and_events() -> None:
    repository = InMemoryRatingRepository()
    publisher = InMemoryDomainEventPublisher(service_name="ranking-service", context="ranking")

    result = RecalculatePlayerRating(repository, publisher).execute(
        RecalculatePlayerRatingCommand(
            match_id=MATCH_ID,
            winner_id=WINNER_ID,
            loser_id=LOSER_ID,
        )
    )

    assert result.created is True
    assert result.winner_rating.score == 1016
    assert result.loser_rating.score == 984
    assert repository.find_by_player_id(WINNER_ID) == result.winner_rating
    assert repository.find_by_player_id(LOSER_ID) == result.loser_rating
    assert [event.name for event in result.events] == [
        "PlayerRankUpdated",
        "PlayerRankUpdated",
    ]
    assert publisher.published_events()[0].payload["delta"] == 16
    assert publisher.published_events()[1].payload["delta"] == -16


def test_recalculate_player_rating_is_idempotent_for_same_match() -> None:
    repository = InMemoryRatingRepository()
    publisher = InMemoryDomainEventPublisher(service_name="ranking-service", context="ranking")
    use_case = RecalculatePlayerRating(repository, publisher)
    command = RecalculatePlayerRatingCommand(
        match_id=MATCH_ID,
        winner_id=WINNER_ID,
        loser_id=LOSER_ID,
    )

    first = use_case.execute(command)
    second = use_case.execute(command)

    assert first.created is True
    assert second.created is False
    assert second.winner_rating.score == 1016
    assert second.loser_rating.score == 984
    assert second.events == ()
    assert len(publisher.published_events()) == 2


def test_get_global_ranking_uses_cache_after_first_query() -> None:
    repository = InMemoryRatingRepository()
    cache = InMemoryLeaderboardCache()
    repository.save_many(
        (
            rating(WINNER_ID, score=1200, wins=2),
            rating(LOSER_ID, score=1100, wins=1),
        )
    )
    use_case = GetGlobalRanking(repository, cache)

    first = use_case.execute(GetGlobalRankingQuery(limit=10, offset=0))
    second = use_case.execute(GetGlobalRankingQuery(limit=10, offset=0))

    assert first.cache_hit is False
    assert second.cache_hit is True
    assert [entry.rating.player_id for entry in second.entries] == [WINNER_ID, LOSER_ID]


def test_get_global_ranking_cache_key_changes_after_rating_update() -> None:
    repository = InMemoryRatingRepository()
    cache = InMemoryLeaderboardCache()
    repository.save_many((rating(WINNER_ID, score=1200),))
    use_case = GetGlobalRanking(repository, cache)
    first = use_case.execute(GetGlobalRankingQuery())

    repository.save_many((rating(LOSER_ID, score=1300),))
    second = use_case.execute(GetGlobalRankingQuery())

    assert first.cache_key != second.cache_key
    assert second.cache_hit is False
    assert second.entries[0].rating.player_id == LOSER_ID


def test_get_friends_ranking_returns_empty_without_friend_ids() -> None:
    repository = InMemoryRatingRepository()
    cache = InMemoryLeaderboardCache()
    repository.save_many((rating(LOSER_ID, score=1300),))

    result = GetFriendsRanking(repository, cache).execute(
        GetFriendsRankingQuery(player_id=WINNER_ID)
    )

    assert result.entries == ()
    assert result.total == 0


def test_get_friends_ranking_filters_supplied_friend_ids() -> None:
    repository = InMemoryRatingRepository()
    cache = InMemoryLeaderboardCache()
    repository.save_many(
        (
            rating(WINNER_ID, score=1000),
            rating(LOSER_ID, score=1300),
        )
    )

    result = GetFriendsRanking(repository, cache).execute(
        GetFriendsRankingQuery(player_id=WINNER_ID, friend_ids=(LOSER_ID,))
    )

    assert result.total == 1
    assert result.entries[0].rating.player_id == LOSER_ID


def rating(player_id: UUID, *, score: int, wins: int = 0) -> Rating:
    return Rating(
        player_id=player_id,
        score=score,
        wins=wins,
        updated_at=datetime(2026, 6, 16, tzinfo=UTC),
    )
