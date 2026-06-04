from threading import Lock
from uuid import UUID

from app.domain.entities import Match


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
