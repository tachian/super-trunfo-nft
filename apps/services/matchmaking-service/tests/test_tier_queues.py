import pytest
from app.application.use_cases import ConfigureTierQueues, GetQueueStatus
from app.domain.entities import MatchmakingTier, TierQueue, configured_tier_queues
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
    queues = ConfigureTierQueues(repository).execute()
    repository.enqueue_ticket(queues[0], "ticket-1")
    repository.enqueue_ticket(queues[0], "ticket-2")
    repository.enqueue_ticket(queues[1], "ticket-3")

    result = GetQueueStatus(repository).execute()

    assert [(item.queue.name, item.size) for item in result.queues] == [
        ("queue:bronze", 2),
        ("queue:silver", 1),
        ("queue:gold", 0),
    ]
