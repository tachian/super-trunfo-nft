from dataclasses import dataclass
from typing import Protocol

from .entities import MatchmakingTicket, TierQueue


@dataclass(frozen=True)
class QueueStatus:
    queue: TierQueue
    size: int


class MatchmakingQueueRepository(Protocol):
    def ensure_queues(self, queues: tuple[TierQueue, ...]) -> None:
        """Ensure tier queues exist in the queue backend."""

    def queue_size(self, queue: TierQueue) -> int:
        """Return the number of tickets waiting in a tier queue."""

    def enqueue_ticket(self, ticket: MatchmakingTicket) -> None:
        """Add a ticket to its tier queue."""

    def find_compatible_ticket(
        self,
        ticket: MatchmakingTicket,
        tolerance: int,
    ) -> MatchmakingTicket | None:
        """Find and remove a compatible waiting ticket from the same tier queue."""
