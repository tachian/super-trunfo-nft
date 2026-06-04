from uuid import UUID

from app.application.use_cases import RequestMatch, RequestMatchCommand
from app.infrastructure.repositories import InMemoryMatchmakingQueueRepository


def test_request_match_queues_player_when_no_compatible_opponent_exists() -> None:
    repository = InMemoryMatchmakingQueueRepository()

    result = RequestMatch(repository).execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
        )
    )

    assert result.status == "queued"
    assert result.matched_ticket is None
    assert result.ticket.tier == "bronze"
    assert repository.queue_size(result.ticket_queue) == 1


def test_request_match_pairs_players_within_level_tolerance() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    use_case = RequestMatch(repository)
    first = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
        )
    )

    second = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("22222222-2222-4222-8222-000000000402"),
            average_deck_level=340,
        )
    )

    assert first.status == "queued"
    assert second.status == "matched"
    assert second.matched_ticket == first.ticket
    assert repository.queue_size(first.ticket_queue) == 0


def test_request_match_does_not_pair_players_outside_tolerance() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    use_case = RequestMatch(repository)
    first = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
        )
    )

    second = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("22222222-2222-4222-8222-000000000402"),
            average_deck_level=341,
        )
    )

    assert first.status == "queued"
    assert second.status == "queued"
    assert second.matched_ticket is None
    assert repository.queue_size(first.ticket_queue) == 2
