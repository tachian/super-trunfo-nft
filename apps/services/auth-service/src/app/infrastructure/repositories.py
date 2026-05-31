from threading import Lock

from app.domain.entities import Player


class InMemoryPlayerRepository:
    def __init__(self) -> None:
        self._players_by_email: dict[str, Player] = {}
        self._players_by_nickname: dict[str, Player] = {}
        self._lock = Lock()

    def add(self, player: Player) -> None:
        with self._lock:
            self._players_by_email[player.email.lower()] = player
            self._players_by_nickname[player.nickname.lower()] = player

    def find_by_email(self, email: str) -> Player | None:
        return self._players_by_email.get(email.lower())

    def find_by_nickname(self, nickname: str) -> Player | None:
        return self._players_by_nickname.get(nickname.lower())

    def clear(self) -> None:
        with self._lock:
            self._players_by_email.clear()
            self._players_by_nickname.clear()
