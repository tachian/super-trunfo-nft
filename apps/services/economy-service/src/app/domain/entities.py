from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .exceptions import EconomyInvariantError

VICTORY_CREDITS = 1
DEFEAT_CREDITS = 0


class MatchResult(StrEnum):
    VICTORY = "victory"
    DEFEAT = "defeat"


class CreditLedgerReason(StrEnum):
    MATCH_VICTORY = "match_victory"
    MATCH_DEFEAT = "match_defeat"


@dataclass(frozen=True)
class ShopOffer:
    id: UUID
    card_id: UUID
    card_name: str
    family: str
    rarity: int
    price: int
    expires_at: datetime

    def __post_init__(self) -> None:
        if not self.card_name.strip():
            raise EconomyInvariantError("shop offer card name cannot be empty")

        if not self.family.strip():
            raise EconomyInvariantError("shop offer family cannot be empty")

        if self.rarity < 0 or self.rarity > 100:
            raise EconomyInvariantError("shop offer rarity must be between 0 and 100")

        if self.price <= 0:
            raise EconomyInvariantError("shop offer price must be positive")

    def is_active(self, now: datetime | None = None) -> bool:
        checked_at = now or datetime.now(UTC)

        return self.expires_at > checked_at


@dataclass(frozen=True)
class CreditLedgerEntry:
    id: UUID
    player_id: UUID
    match_id: UUID
    amount: int
    reason: CreditLedgerReason
    created_at: datetime

    def __post_init__(self) -> None:
        normalized_reason = CreditLedgerReason(self.reason)

        if self.amount < 0:
            raise EconomyInvariantError("credit ledger amount cannot be negative")

        if normalized_reason == CreditLedgerReason.MATCH_VICTORY and self.amount != VICTORY_CREDITS:
            raise EconomyInvariantError("match victory must grant one credit")

        if normalized_reason == CreditLedgerReason.MATCH_DEFEAT and self.amount != DEFEAT_CREDITS:
            raise EconomyInvariantError("match defeat must grant zero credits")

        object.__setattr__(self, "reason", normalized_reason)


@dataclass(frozen=True)
class InventoryCard:
    id: UUID
    player_id: UUID
    card_id: UUID
    source_offer_id: UUID
    acquired_at: datetime


@dataclass(frozen=True)
class Purchase:
    id: UUID
    player_id: UUID
    offer_id: UUID
    card_id: UUID
    price: int
    purchased_at: datetime

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise EconomyInvariantError("purchase price must be positive")


@dataclass(frozen=True)
class Wallet:
    player_id: UUID
    balance: int
    ledger_entries: tuple[CreditLedgerEntry, ...] = ()
    purchases: tuple[Purchase, ...] = ()
    inventory_cards: tuple[InventoryCard, ...] = ()

    def __post_init__(self) -> None:
        if self.balance < 0:
            raise EconomyInvariantError("wallet balance cannot be negative")

        if any(entry.player_id != self.player_id for entry in self.ledger_entries):
            raise EconomyInvariantError("wallet ledger entry must belong to wallet player")

        if any(purchase.player_id != self.player_id for purchase in self.purchases):
            raise EconomyInvariantError("wallet purchase must belong to wallet player")

        if any(card.player_id != self.player_id for card in self.inventory_cards):
            raise EconomyInvariantError("wallet inventory card must belong to wallet player")

        credit_total = sum(entry.amount for entry in self.ledger_entries)
        purchase_total = sum(purchase.price for purchase in self.purchases)

        if credit_total - purchase_total != self.balance:
            raise EconomyInvariantError("wallet balance must match credits minus purchases")

        match_ids = [entry.match_id for entry in self.ledger_entries]

        if len(match_ids) != len(set(match_ids)):
            raise EconomyInvariantError("wallet ledger cannot contain duplicated match result")

        offer_ids = [purchase.offer_id for purchase in self.purchases]

        if len(offer_ids) != len(set(offer_ids)):
            raise EconomyInvariantError("wallet purchases cannot contain duplicated offer")

        inventory_card_ids = [card.card_id for card in self.inventory_cards]

        if len(inventory_card_ids) != len(set(inventory_card_ids)):
            raise EconomyInvariantError("wallet inventory cannot contain duplicated card")

    def apply_match_result(
        self,
        *,
        match_id: UUID,
        result: MatchResult | str,
        created_at: datetime | None = None,
        ledger_entry_id: UUID | None = None,
    ) -> tuple["Wallet", CreditLedgerEntry, bool]:
        for entry in self.ledger_entries:
            if entry.match_id == match_id:
                return self, entry, False

        amount = credits_for_match_result(result)
        reason = reason_for_match_result(result)
        entry = CreditLedgerEntry(
            id=ledger_entry_id or uuid4(),
            player_id=self.player_id,
            match_id=match_id,
            amount=amount,
            reason=reason,
            created_at=created_at or datetime.now(UTC),
        )

        return (
            Wallet(
                player_id=self.player_id,
                balance=self.balance + entry.amount,
                ledger_entries=(*self.ledger_entries, entry),
                purchases=self.purchases,
                inventory_cards=self.inventory_cards,
            ),
            entry,
            True,
        )

    def buy_offer(
        self,
        *,
        offer: ShopOffer,
        purchased_at: datetime | None = None,
        purchase_id: UUID | None = None,
        inventory_card_id: UUID | None = None,
    ) -> tuple["Wallet", Purchase, InventoryCard]:
        checked_at = purchased_at or datetime.now(UTC)

        if not offer.is_active(checked_at):
            raise EconomyInvariantError("shop offer has expired")

        if self.balance < offer.price:
            raise EconomyInvariantError("wallet has insufficient credits")

        if any(purchase.offer_id == offer.id for purchase in self.purchases):
            raise EconomyInvariantError("shop offer was already purchased")

        purchase = Purchase(
            id=purchase_id or uuid4(),
            player_id=self.player_id,
            offer_id=offer.id,
            card_id=offer.card_id,
            price=offer.price,
            purchased_at=checked_at,
        )
        inventory_card = InventoryCard(
            id=inventory_card_id or uuid4(),
            player_id=self.player_id,
            card_id=offer.card_id,
            source_offer_id=offer.id,
            acquired_at=checked_at,
        )

        return (
            Wallet(
                player_id=self.player_id,
                balance=self.balance - offer.price,
                ledger_entries=self.ledger_entries,
                purchases=(*self.purchases, purchase),
                inventory_cards=(*self.inventory_cards, inventory_card),
            ),
            purchase,
            inventory_card,
        )


def create_wallet(player_id: UUID) -> Wallet:
    return Wallet(player_id=player_id, balance=0)


def credits_for_match_result(result: MatchResult | str) -> int:
    normalized_result = MatchResult(result)

    if normalized_result == MatchResult.VICTORY:
        return VICTORY_CREDITS

    return DEFEAT_CREDITS


def reason_for_match_result(result: MatchResult | str) -> CreditLedgerReason:
    normalized_result = MatchResult(result)

    if normalized_result == MatchResult.VICTORY:
        return CreditLedgerReason.MATCH_VICTORY

    return CreditLedgerReason.MATCH_DEFEAT
