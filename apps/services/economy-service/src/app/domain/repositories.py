from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import Wallet


class WalletRepository(Protocol):
    def save(self, wallet: Wallet) -> None:
        """Persist wallet state."""

    def find_by_player_id(self, player_id: UUID) -> Wallet | None:
        """Find a wallet by player id."""


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""

