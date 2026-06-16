from uuid import UUID

from app.application.use_cases import (
    RecalculatePlayerRating,
    RecalculatePlayerRatingCommand,
)
from app.infrastructure.repositories import InMemoryRatingRepository
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
