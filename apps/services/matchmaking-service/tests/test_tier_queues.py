from uuid import UUID, uuid4

import pytest
from app.application.use_cases import ConfigureTierQueues, GetQueueStatus
from app.domain.entities import (
    MatchmakingTicket,
    MatchmakingTier,
    TierQueue,
    configured_tier_queues,
    tier_for_average_level,
)
from app.domain.exceptions import MatchmakingInvariantError
from app.infrastructure.repositories import InMemoryMatchmakingQueueRepository


def test_configured_tier_queues_match_redis_names() -> None:
    queues = configured_tier_queues()

    assert [queue.tier for queue in queues] == [
        MatchmakingTier.BRONZE,
        MatchmakingTier.SILVER,
        MatchmakingTier.GOLD,
    ]
    assert [queue.name for queue in queues] == [
        "queue:bronze",
        "queue:silver",
        "queue:gold",
    ]


def test_tier_queue_rejects_name_that_does_not_match_tier() -> None:
    with pytest.raises(MatchmakingInvariantError, match="queue name"):
        TierQueue(tier=MatchmakingTier.BRONZE, name="queue:gold")


def test_configure_tier_queues_creates_all_queues() -> None:
    repository = InMemoryMatchmakingQueueRepository()

    queues = ConfigureTierQueues(repository).execute()

    assert repository.configured_queue_names() == tuple(queue.name for queue in queues)


def test_get_queue_status_returns_queue_sizes() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    ConfigureTierQueues(repository).execute()
    repository.enqueue_ticket(ticket("11111111-1111-4111-8111-000000000401", 320))
    repository.enqueue_ticket(ticket("11111111-1111-4111-8111-000000000402", 330))
    repository.enqueue_ticket(ticket("11111111-1111-4111-8111-000000000403", 1100))

    result = GetQueueStatus(repository).execute()

    assert [(item.queue.name, item.size) for item in result.queues] == [
        ("queue:bronze", 2),
        ("queue:silver", 1),
        ("queue:gold", 0),
    ]


def test_tier_for_average_level_uses_configured_ranges() -> None:
    assert tier_for_average_level(999) == MatchmakingTier.BRONZE
    assert tier_for_average_level(1000) == MatchmakingTier.SILVER
    assert tier_for_average_level(1499) == MatchmakingTier.SILVER
    assert tier_for_average_level(1500) == MatchmakingTier.GOLD


def test_repository_finds_and_removes_compatible_ticket() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    ConfigureTierQueues(repository).execute()
    waiting_ticket = ticket("11111111-1111-4111-8111-000000000401", 320)
    request_ticket = ticket("22222222-2222-4222-8222-000000000401", 339)
    repository.enqueue_ticket(waiting_ticket)

    matched_ticket = repository.find_compatible_ticket(request_ticket, tolerance=20)

    assert matched_ticket == waiting_ticket
    assert repository.queue_size(queues_by_name()["queue:bronze"]) == 0


def test_repository_keeps_incompatible_ticket_in_queue() -> None:
    repository = InMemoryMatchmakingQueueRepository()
    ConfigureTierQueues(repository).execute()
    waiting_ticket = ticket("11111111-1111-4111-8111-000000000401", 320)
    request_ticket = ticket("22222222-2222-4222-8222-000000000401", 341)
    repository.enqueue_ticket(waiting_ticket)

    matched_ticket = repository.find_compatible_ticket(request_ticket, tolerance=20)

    assert matched_ticket is None
    assert repository.queue_size(queues_by_name()["queue:bronze"]) == 1


def ticket(player_id: str, average_deck_level: int) -> MatchmakingTicket:
    return MatchmakingTicket(
        id=uuid4(),
        player_id=UUID(player_id),
        average_deck_level=average_deck_level,
        tier=tier_for_average_level(average_deck_level),
    )


def queues_by_name() -> dict[str, TierQueue]:
    return {queue.name: queue for queue in configured_tier_queues()}
