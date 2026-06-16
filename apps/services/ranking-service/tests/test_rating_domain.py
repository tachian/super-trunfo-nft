from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.domain.entities import (
    RankingTier,
    Rating,
    create_rating,
    expected_score,
    leaderboard_entries,
    recalculate_elo_ratings,
    tier_for_score,
)
from app.domain.exceptions import RankingInvariantError

WINNER_ID = UUID("11111111-1111-4111-8111-000000000503")
LOSER_ID = UUID("22222222-2222-4222-8222-000000000503")
MATCH_ID = UUID("33333333-3333-4333-8333-000000000503")


def test_equal_rating_match_gives_winner_sixteen_points() -> None:
    winner = create_rating(WINNER_ID)
    loser = create_rating(LOSER_ID)

    updated_winner, updated_loser, created = recalculate_elo_ratings(
        winner=winner,
        loser=loser,
        match_id=MATCH_ID,
    )

    assert created is True
    assert updated_winner.score == 1016
    assert updated_loser.score == 984
    assert updated_winner.wins == 1
    assert updated_loser.losses == 1
    assert updated_winner.tier == RankingTier.SILVER
    assert updated_loser.tier == RankingTier.BRONZE


def test_rating_recalculation_is_idempotent_per_match() -> None:
    winner = create_rating(WINNER_ID)
    loser = create_rating(LOSER_ID)
    updated_winner, updated_loser, _ = recalculate_elo_ratings(
        winner=winner,
        loser=loser,
        match_id=MATCH_ID,
    )

    duplicate_winner, duplicate_loser, created = recalculate_elo_ratings(
        winner=updated_winner,
        loser=updated_loser,
        match_id=MATCH_ID,
    )

    assert created is False
    assert duplicate_winner == updated_winner
    assert duplicate_loser == updated_loser


def test_rating_recalculation_rejects_same_winner_and_loser() -> None:
    rating = create_rating(WINNER_ID)

    with pytest.raises(RankingInvariantError, match="different players"):
        recalculate_elo_ratings(winner=rating, loser=rating, match_id=MATCH_ID)


def test_tier_for_score_uses_mvp_ranges() -> None:
    assert tier_for_score(0) == RankingTier.BRONZE
    assert tier_for_score(999) == RankingTier.BRONZE
    assert tier_for_score(1000) == RankingTier.SILVER
    assert tier_for_score(1499) == RankingTier.SILVER
    assert tier_for_score(1500) == RankingTier.GOLD
    assert tier_for_score(1999) == RankingTier.GOLD
    assert tier_for_score(2000) == RankingTier.PLATINUM
    assert tier_for_score(2499) == RankingTier.PLATINUM
    assert tier_for_score(2500) == RankingTier.DIAMOND


def test_expected_score_is_balanced_for_equal_ratings() -> None:
    assert expected_score(1000, 1000) == 0.5


def test_leaderboard_entries_order_by_score_and_position() -> None:
    ratings = (
        rating(UUID("44444444-4444-4444-8444-000000000503"), score=1200, wins=2),
        rating(UUID("55555555-5555-4555-8555-000000000503"), score=1300, wins=1),
        rating(UUID("66666666-6666-4666-8666-000000000503"), score=1200, wins=3),
    )

    entries = leaderboard_entries(ratings)

    assert [entry.position for entry in entries] == [1, 2, 3]
    assert [entry.rating.score for entry in entries] == [1300, 1200, 1200]
    assert entries[1].rating.wins == 3


def test_leaderboard_entries_support_offset_and_limit() -> None:
    ratings = (
        rating(UUID("44444444-4444-4444-8444-000000000503"), score=1200),
        rating(UUID("55555555-5555-4555-8555-000000000503"), score=1300),
        rating(UUID("66666666-6666-4666-8666-000000000503"), score=1100),
    )

    entries = leaderboard_entries(ratings, offset=1, limit=1)

    assert len(entries) == 1
    assert entries[0].position == 2
    assert entries[0].rating.score == 1200


def rating(player_id: UUID, *, score: int, wins: int = 0) -> Rating:
    return Rating(
        player_id=player_id,
        score=score,
        wins=wins,
        updated_at=datetime(2026, 6, 16, tzinfo=UTC),
    )
