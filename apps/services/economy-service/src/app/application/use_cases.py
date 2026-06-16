from dataclasses import dataclass
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import (
    CreditLedgerEntry,
    InventoryCard,
    MatchResult,
    Purchase,
    ShopOffer,
    Wallet,
    create_wallet,
)
from app.domain.events import credits_earned_event, offer_purchased_event
from app.domain.exceptions import (
    InsufficientCreditsError,
    ShopOfferExpiredError,
    ShopOfferNotFoundError,
    WalletNotFoundError,
)
from app.domain.repositories import (
    DomainEventPublisher,
    ShopOfferRepository,
    WalletRepository,
)


@dataclass(frozen=True)
class ApplyMatchResultCommand:
    player_id: UUID
    match_id: UUID
    result: MatchResult


@dataclass(frozen=True)
class ApplyMatchResultResult:
    wallet: Wallet
    ledger_entry: CreditLedgerEntry
    created: bool
    events: tuple[DomainEvent, ...]


@dataclass(frozen=True)
class GetWalletCreditsQuery:
    player_id: UUID


@dataclass(frozen=True)
class ListShopOffersResult:
    offers: tuple[ShopOffer, ...]


@dataclass(frozen=True)
class BuyShopOfferCommand:
    player_id: UUID
    offer_id: UUID


@dataclass(frozen=True)
class BuyShopOfferResult:
    wallet: Wallet
    offer: ShopOffer
    purchase: Purchase
    inventory_card: InventoryCard
    events: tuple[DomainEvent, ...]


class ApplyMatchResultCredits:
    def __init__(
        self,
        repository: WalletRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: ApplyMatchResultCommand) -> ApplyMatchResultResult:
        wallet = self.repository.find_by_player_id(command.player_id) or create_wallet(
            command.player_id
        )
        updated_wallet, ledger_entry, created = wallet.apply_match_result(
            match_id=command.match_id,
            result=command.result,
        )
        self.repository.save(updated_wallet)

        events: tuple[DomainEvent, ...] = ()

        if created and ledger_entry.amount > 0:
            event = credits_earned_event(updated_wallet, ledger_entry)
            self.event_publisher.publish(event)
            events = (event,)

        return ApplyMatchResultResult(
            wallet=updated_wallet,
            ledger_entry=ledger_entry,
            created=created,
            events=events,
        )


class GetWalletCredits:
    def __init__(self, repository: WalletRepository) -> None:
        self.repository = repository

    def execute(self, query: GetWalletCreditsQuery) -> Wallet:
        wallet = self.repository.find_by_player_id(query.player_id)

        if wallet is None:
            raise WalletNotFoundError("wallet was not found")

        return wallet


class ListShopOffers:
    def __init__(self, repository: ShopOfferRepository) -> None:
        self.repository = repository

    def execute(self) -> ListShopOffersResult:
        return ListShopOffersResult(offers=self.repository.list_active())


class BuyShopOffer:
    def __init__(
        self,
        wallet_repository: WalletRepository,
        shop_offer_repository: ShopOfferRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.wallet_repository = wallet_repository
        self.shop_offer_repository = shop_offer_repository
        self.event_publisher = event_publisher

    def execute(self, command: BuyShopOfferCommand) -> BuyShopOfferResult:
        wallet = self.wallet_repository.find_by_player_id(command.player_id)

        if wallet is None:
            raise WalletNotFoundError("wallet was not found")

        offer = self.shop_offer_repository.find_by_id(command.offer_id)

        if offer is None:
            raise ShopOfferNotFoundError("shop offer was not found")

        if not offer.is_active():
            raise ShopOfferExpiredError("shop offer has expired")

        if wallet.balance < offer.price:
            raise InsufficientCreditsError("wallet has insufficient credits")

        updated_wallet, purchase, inventory_card = wallet.buy_offer(offer=offer)
        self.wallet_repository.save(updated_wallet)

        event = offer_purchased_event(updated_wallet, purchase, inventory_card, offer)
        self.event_publisher.publish(event)

        return BuyShopOfferResult(
            wallet=updated_wallet,
            offer=offer,
            purchase=purchase,
            inventory_card=inventory_card,
            events=(event,),
        )
