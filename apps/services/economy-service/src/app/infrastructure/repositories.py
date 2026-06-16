from datetime import UTC, datetime, timedelta
from threading import Lock
from uuid import UUID

from app.domain.entities import ShopOffer, Wallet


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


class InMemoryShopOfferRepository:
    def __init__(self, offers: tuple[ShopOffer, ...] = ()) -> None:
        self._offers_by_id: dict[UUID, ShopOffer] = {
            offer.id: offer for offer in offers
        }
        self._lock = Lock()

    @classmethod
    def with_default_offers(cls) -> "InMemoryShopOfferRepository":
        expires_at = datetime.now(UTC) + timedelta(days=7)

        return cls(
            offers=(
                ShopOffer(
                    id=UUID("11111111-5020-4502-8502-000000000001"),
                    card_id=UUID("22222222-5020-4502-8502-000000000001"),
                    card_name="Capitao Nebula",
                    family="cosmic",
                    rarity=64,
                    price=1,
                    expires_at=expires_at,
                ),
                ShopOffer(
                    id=UUID("11111111-5020-4502-8502-000000000002"),
                    card_id=UUID("22222222-5020-4502-8502-000000000002"),
                    card_name="Guardia Lumen",
                    family="guardian",
                    rarity=58,
                    price=2,
                    expires_at=expires_at,
                ),
            )
        )

    def save(self, offer: ShopOffer) -> None:
        with self._lock:
            self._offers_by_id[offer.id] = offer

    def list_active(self) -> tuple[ShopOffer, ...]:
        with self._lock:
            offers = tuple(self._offers_by_id.values())

        return tuple(offer for offer in offers if offer.is_active())

    def find_by_id(self, offer_id: UUID) -> ShopOffer | None:
        return self._offers_by_id.get(offer_id)

    def clear(self) -> None:
        with self._lock:
            self._offers_by_id.clear()
