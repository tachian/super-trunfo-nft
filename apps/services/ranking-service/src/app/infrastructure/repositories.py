from threading import Lock
from uuid import UUID

from app.domain.entities import LeaderboardEntry, Rating, Season, SeasonStatus


class InMemoryRatingRepository:
    def __init__(self) -> None:
        self._ratings_by_player_id: dict[UUID, Rating] = {}
        self._version = 0
        self._lock = Lock()

    def save_many(self, ratings: tuple[Rating, ...]) -> None:
        with self._lock:
            for rating in ratings:
                self._ratings_by_player_id[rating.player_id] = rating
            self._version += 1

    def find_by_player_id(self, player_id: UUID) -> Rating | None:
        return self._ratings_by_player_id.get(player_id)

    def list_all(self) -> tuple[Rating, ...]:
        with self._lock:
            return tuple(self._ratings_by_player_id.values())

    def version(self) -> int:
        return self._version

    def clear(self) -> None:
        with self._lock:
            self._ratings_by_player_id.clear()
            self._version += 1


class InMemorySeasonRepository:
    def __init__(self) -> None:
        self._seasons_by_id: dict[UUID, Season] = {}
        self._lock = Lock()

    def save(self, season: Season) -> None:
        with self._lock:
            self._seasons_by_id[season.id] = season

    def find_by_id(self, season_id: UUID) -> Season | None:
        return self._seasons_by_id.get(season_id)

    def find_current(self) -> Season | None:
        with self._lock:
            seasons = tuple(self._seasons_by_id.values())

        active_seasons = tuple(
            season for season in seasons if season.status == SeasonStatus.ACTIVE
        )

        if not active_seasons:
            return None

        return sorted(active_seasons, key=lambda season: season.starts_at, reverse=True)[0]

    def clear(self) -> None:
        with self._lock:
            self._seasons_by_id.clear()


class InMemoryLeaderboardCache:
    def __init__(self) -> None:
        self._entries_by_key: dict[str, tuple[LeaderboardEntry, ...]] = {}
        self._lock = Lock()

    def get(self, key: str) -> tuple[LeaderboardEntry, ...] | None:
        return self._entries_by_key.get(key)

    def set(self, key: str, entries: tuple[LeaderboardEntry, ...]) -> None:
        with self._lock:
            self._entries_by_key[key] = entries

    def clear(self) -> None:
        with self._lock:
            self._entries_by_key.clear()
