from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import ShopOffer, Wallet


class WalletRepository(Protocol):
    def save(self, wallet: Wallet) -> None:
        """Persist wallet state."""

    def find_by_player_id(self, player_id: UUID) -> Wallet | None:
        """Find a wallet by player id."""

    def list_all(self) -> tuple[Wallet, ...]:
        """List all wallets for telemetry and operational views."""


class ShopOfferRepository(Protocol):
    def list_active(self) -> tuple[ShopOffer, ...]:
        """List active shop offers."""

    def find_by_id(self, offer_id: UUID) -> ShopOffer | None:
        """Find a shop offer by id."""


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
