from threading import Lock
from uuid import UUID

from app.domain.entities import GameplayRealtimeEvent, Match


class InMemoryMatchRepository:
    def __init__(self) -> None:
        self._matches_by_id: dict[UUID, Match] = {}
        self._lock = Lock()

    def save(self, match: Match) -> None:
        with self._lock:
            self._matches_by_id[match.id] = match

    def find_by_id(self, match_id: UUID) -> Match | None:
        return self._matches_by_id.get(match_id)

    def clear(self) -> None:
        with self._lock:
            self._matches_by_id.clear()


class InMemoryGameplayRealtimeEventBus:
    def __init__(self) -> None:
        self._events_by_match_id: dict[UUID, list[GameplayRealtimeEvent]] = {}
        self._lock = Lock()

    def publish(self, event: GameplayRealtimeEvent) -> None:
        with self._lock:
            self._events_by_match_id.setdefault(event.match_id, []).append(event)

    def events_for_match(
        self,
        match_id: UUID,
        after_index: int = 0,
    ) -> tuple[GameplayRealtimeEvent, ...]:
        with self._lock:
            events = self._events_by_match_id.get(match_id, [])
            return tuple(events[after_index:])

    def clear(self) -> None:
        with self._lock:
            self._events_by_match_id.clear()
