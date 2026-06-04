from threading import Lock

from app.domain.entities import (
    MatchmakingTicket,
    MatchStartedEvent,
    TierQueue,
    queue_name_for_tier,
)


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


class InMemoryMatchmakingEventPublisher:
    """In-memory event publisher for local tests and service bootstrapping."""

    def __init__(self) -> None:
        self._events: list[MatchStartedEvent] = []
        self._lock = Lock()

    def publish(self, event: MatchStartedEvent) -> None:
        with self._lock:
            self._events.append(event)

    def published_events(self) -> tuple[MatchStartedEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
