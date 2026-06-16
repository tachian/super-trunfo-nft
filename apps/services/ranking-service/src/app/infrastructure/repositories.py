from threading import Lock
from uuid import UUID

from app.domain.entities import Rating


class InMemoryRatingRepository:
    def __init__(self) -> None:
        self._ratings_by_player_id: dict[UUID, Rating] = {}
        self._lock = Lock()

    def save_many(self, ratings: tuple[Rating, ...]) -> None:
        with self._lock:
            for rating in ratings:
                self._ratings_by_player_id[rating.player_id] = rating

    def find_by_player_id(self, player_id: UUID) -> Rating | None:
        return self._ratings_by_player_id.get(player_id)

    def clear(self) -> None:
        with self._lock:
            self._ratings_by_player_id.clear()
