from dataclasses import dataclass
from typing import Protocol

from .entities import TierQueue


@dataclass(frozen=True)
class QueueStatus:
    queue: TierQueue
    size: int


class MatchmakingQueueRepository(Protocol):
    def ensure_queues(self, queues: tuple[TierQueue, ...]) -> None:
        """Ensure tier queues exist in the queue backend."""

    def queue_size(self, queue: TierQueue) -> int:
        """Return the number of tickets waiting in a tier queue."""
