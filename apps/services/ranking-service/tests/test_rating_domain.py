from uuid import UUID

import pytest
from app.domain.entities import (
    RankingTier,
    create_rating,
    expected_score,
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
