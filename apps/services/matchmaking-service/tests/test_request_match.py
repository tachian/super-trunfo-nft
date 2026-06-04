from uuid import UUID

from app.application.use_cases import RequestMatch, RequestMatchCommand
from app.infrastructure.repositories import (
    InMemoryMatchmakingEventPublisher,
    InMemoryMatchmakingQueueRepository,
)


def test_request_match_creates_pve_fallback_when_no_compatible_opponent_exists() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    event_publisher = InMemoryMatchmakingEventPublisher()

    result = RequestMatch(repository, event_publisher).execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
        )
    )

    assert result.status == "pve_created"
    assert result.matched_ticket is None
    assert result.ticket.tier == "bronze"
    assert result.match is not None
    assert result.match.mode == "pve"
    assert result.match.opponent.kind == "bot"
    assert result.match.opponent.average_deck_level == result.ticket.average_deck_level
    assert repository.queue_size(result.ticket_queue) == 0
    assert event_publisher.published_events()[0].name == "MatchStarted"
    assert event_publisher.published_events()[0].opponent_kind == "bot"


def test_request_match_queues_player_when_fallback_timeout_is_configured() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    event_publisher = InMemoryMatchmakingEventPublisher()

    result = RequestMatch(repository, event_publisher).execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
            fallback_after_seconds=10,
        )
    )

    assert result.status == "queued"
    assert result.match is None
    assert result.fallback_after_seconds == 10
    assert repository.queue_size(result.ticket_queue) == 1
    assert event_publisher.published_events() == ()


def test_request_match_pairs_players_within_level_tolerance() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    event_publisher = InMemoryMatchmakingEventPublisher()
    use_case = RequestMatch(repository, event_publisher)
    first = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
            fallback_after_seconds=10,
        )
    )

    second = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("22222222-2222-4222-8222-000000000402"),
            average_deck_level=340,
            fallback_after_seconds=10,
        )
    )

    assert first.status == "queued"
    assert second.status == "matched"
    assert second.matched_ticket == first.ticket
    assert second.match is not None
    assert second.match.mode == "pvp"
    assert second.match.opponent.kind == "player"
    assert repository.queue_size(first.ticket_queue) == 0
    assert event_publisher.published_events()[0].opponent_kind == "player"


def test_request_match_does_not_pair_players_outside_tolerance() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    event_publisher = InMemoryMatchmakingEventPublisher()
    use_case = RequestMatch(repository, event_publisher)
    first = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-000000000402"),
            average_deck_level=320,
            fallback_after_seconds=10,
        )
    )

    second = use_case.execute(
        RequestMatchCommand(
            player_id=UUID("22222222-2222-4222-8222-000000000402"),
            average_deck_level=341,
            fallback_after_seconds=10,
        )
    )

    assert first.status == "queued"
    assert second.status == "queued"
    assert second.matched_ticket is None
    assert repository.queue_size(first.ticket_queue) == 2
    assert event_publisher.published_events() == ()
