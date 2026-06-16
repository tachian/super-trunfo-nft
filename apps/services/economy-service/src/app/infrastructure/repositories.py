from threading import Lock
from uuid import UUID

from app.domain.entities import Wallet


class InMemoryWalletRepository:
    def __init__(self) -> None:
        self._wallets_by_player_id: dict[UUID, Wallet] = {}
        self._lock = Lock()

    def save(self, wallet: Wallet) -> None:
        with self._lock:
            self._wallets_by_player_id[wallet.player_id] = wallet

    def find_by_player_id(self, player_id: UUID) -> Wallet | None:
        return self._wallets_by_player_id.get(player_id)

    def clear(self) -> None:
        with self._lock:
            self._wallets_by_player_id.clear()
