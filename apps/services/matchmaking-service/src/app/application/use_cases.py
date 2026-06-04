from dataclasses import dataclass

from app.domain.entities import TierQueue, configured_tier_queues
from app.domain.repositories import MatchmakingQueueRepository, QueueStatus


@dataclass(frozen=True)
class GetQueueStatusResult:
    queues: tuple[QueueStatus, ...]


class ConfigureTierQueues:
    def __init__(self, repository: MatchmakingQueueRepository) -> None:
        self.repository = repository

    def execute(self) -> tuple[TierQueue, ...]:
        queues = configured_tier_queues()
        self.repository.ensure_queues(queues)

        return queues


class GetQueueStatus:
    def __init__(self, repository: MatchmakingQueueRepository) -> None:
        self.repository = repository

    def execute(self) -> GetQueueStatusResult:
        queues = configured_tier_queues()
        self.repository.ensure_queues(queues)

        return GetQueueStatusResult(
            queues=tuple(
                QueueStatus(
                    queue=queue,
                    size=self.repository.queue_size(queue),
                )
                for queue in queues
            )
        )
