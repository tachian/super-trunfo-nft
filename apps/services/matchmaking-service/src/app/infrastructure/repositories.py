from threading import Lock

from app.domain.entities import MatchmakingTicket, TierQueue, queue_name_for_tier


class InMemoryMatchmakingQueueRepository:
    """In-memory Redis-compatible queue catalog for local tests and service bootstrapping."""

    def __init__(self) -> None:
        self._queues: dict[str, list[MatchmakingTicket]] = {}
        self._lock = Lock()

    def ensure_queues(self, queues: tuple[TierQueue, ...]) -> None:
        with self._lock:
            for queue in queues:
                self._queues.setdefault(queue.name, [])

    def queue_size(self, queue: TierQueue) -> int:
        return len(self._queues.get(queue.name, []))

    def enqueue_ticket(self, ticket: MatchmakingTicket) -> None:
        with self._lock:
            queue_name = queue_name_for_tier(ticket.tier)
            self._queues.setdefault(queue_name, []).append(ticket)

    def find_compatible_ticket(
        self,
        ticket: MatchmakingTicket,
        tolerance: int,
    ) -> MatchmakingTicket | None:
        queue_name = queue_name_for_tier(ticket.tier)

        with self._lock:
            queue = self._queues.setdefault(queue_name, [])

            for index, candidate in enumerate(queue):
                if ticket.is_compatible_with(candidate, tolerance=tolerance):
                    return queue.pop(index)

        return None

    def configured_queue_names(self) -> tuple[str, ...]:
        return tuple(self._queues)

    def clear(self) -> None:
        with self._lock:
            self._queues.clear()
