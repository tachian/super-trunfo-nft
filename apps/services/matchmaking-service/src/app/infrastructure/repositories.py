from threading import Lock

from app.domain.entities import TierQueue


class InMemoryMatchmakingQueueRepository:
    """In-memory Redis-compatible queue catalog for local tests and service bootstrapping."""

    def __init__(self) -> None:
        self._queues: dict[str, list[str]] = {}
        self._lock = Lock()

    def ensure_queues(self, queues: tuple[TierQueue, ...]) -> None:
        with self._lock:
            for queue in queues:
                self._queues.setdefault(queue.name, [])

    def queue_size(self, queue: TierQueue) -> int:
        return len(self._queues.get(queue.name, []))

    def enqueue_ticket(self, queue: TierQueue, ticket_id: str) -> None:
        with self._lock:
            self._queues.setdefault(queue.name, []).append(ticket_id)

    def configured_queue_names(self) -> tuple[str, ...]:
        return tuple(self._queues)

    def clear(self) -> None:
        with self._lock:
            self._queues.clear()
