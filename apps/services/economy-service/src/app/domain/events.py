from super_trunfo_shared import DomainEvent

from .entities import CreditLedgerEntry, InventoryCard, Purchase, ShopOffer, Wallet


def credits_earned_event(wallet: Wallet, entry: CreditLedgerEntry) -> DomainEvent:
    return DomainEvent(
        name="CreditsEarned",
        aggregate_id=str(wallet.player_id),
        occurred_at=entry.created_at,
        payload={
            "schema_version": "1.0.0",
            "player_id": str(wallet.player_id),
            "match_id": str(entry.match_id),
            "ledger_entry_id": str(entry.id),
            "amount": entry.amount,
            "balance": wallet.balance,
            "reason": entry.reason.value,
            "earned_at": entry.created_at.isoformat(),
        },
    )


def offer_purchased_event(
    wallet: Wallet,
    purchase: Purchase,
    inventory_card: InventoryCard,
    offer: ShopOffer,
) -> DomainEvent:
    return DomainEvent(
        name="OfferPurchased",
        aggregate_id=str(wallet.player_id),
        occurred_at=purchase.purchased_at,
        payload={
            "schema_version": "1.0.0",
            "player_id": str(wallet.player_id),
            "offer_id": str(purchase.offer_id),
            "purchase_id": str(purchase.id),
            "inventory_card_id": str(inventory_card.id),
            "card_id": str(purchase.card_id),
            "card_name": offer.card_name,
            "price": purchase.price,
            "balance": wallet.balance,
            "purchased_at": purchase.purchased_at.isoformat(),
        },
    )
