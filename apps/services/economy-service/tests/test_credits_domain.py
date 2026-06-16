from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from app.domain.entities import (
    CreditLedgerEntry,
    CreditLedgerReason,
    MatchResult,
    ShopOffer,
    Wallet,
    create_wallet,
    credits_for_match_result,
)
from app.domain.exceptions import EconomyInvariantError

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000501")
MATCH_ID = UUID("22222222-2222-4222-8222-000000000501")
SHOP_OFFER_ID = UUID("11111111-5020-4502-8502-000000000001")
CARD_ID = UUID("22222222-5020-4502-8502-000000000001")


def test_victory_grants_one_credit() -> None:
    wallet = create_wallet(PLAYER_ID)

    updated_wallet, entry, created = wallet.apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )

    assert created is True
    assert entry.amount == 1
    assert entry.reason == CreditLedgerReason.MATCH_VICTORY
    assert updated_wallet.balance == 1


def test_defeat_grants_zero_credits_but_records_result() -> None:
    wallet = create_wallet(PLAYER_ID)

    updated_wallet, entry, created = wallet.apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.DEFEAT,
    )

    assert created is True
    assert entry.amount == 0
    assert entry.reason == CreditLedgerReason.MATCH_DEFEAT
    assert updated_wallet.balance == 0
    assert updated_wallet.ledger_entries == (entry,)


def test_match_result_is_idempotent_per_wallet() -> None:
    wallet = create_wallet(PLAYER_ID)
    updated_wallet, first_entry, _ = wallet.apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )

    duplicate_wallet, duplicate_entry, created = updated_wallet.apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )

    assert created is False
    assert duplicate_entry == first_entry
    assert duplicate_wallet == updated_wallet
    assert duplicate_wallet.balance == 1


def test_wallet_rejects_duplicated_match_results() -> None:
    wallet = create_wallet(PLAYER_ID)
    updated_wallet, entry, _ = wallet.apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )

    with pytest.raises(EconomyInvariantError, match="duplicated match result"):
        Wallet(
            player_id=PLAYER_ID,
            balance=2,
            ledger_entries=(entry, entry),
        )


def test_credits_for_match_result_uses_mvp_rules() -> None:
    assert credits_for_match_result("victory") == 1
    assert credits_for_match_result("defeat") == 0


def test_ledger_entry_rejects_invalid_victory_amount() -> None:
    with pytest.raises(EconomyInvariantError, match="victory"):
        CreditLedgerEntry(
            id=UUID("33333333-3333-4333-8333-000000000501"),
            player_id=PLAYER_ID,
            match_id=MATCH_ID,
            amount=2,
            reason=CreditLedgerReason.MATCH_VICTORY,
            created_at=create_wallet(PLAYER_ID)
            .apply_match_result(match_id=MATCH_ID, result=MatchResult.VICTORY)[1]
            .created_at,
        )


def test_wallet_buy_offer_debits_balance_and_adds_inventory_card() -> None:
    wallet, _, _ = create_wallet(PLAYER_ID).apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )
    offer = active_offer(price=1)

    updated_wallet, purchase, inventory_card = wallet.buy_offer(offer=offer)

    assert updated_wallet.balance == 0
    assert purchase.offer_id == offer.id
    assert purchase.price == 1
    assert inventory_card.card_id == offer.card_id
    assert updated_wallet.purchases == (purchase,)
    assert updated_wallet.inventory_cards == (inventory_card,)


def test_wallet_buy_offer_rejects_insufficient_credits() -> None:
    wallet = create_wallet(PLAYER_ID)

    with pytest.raises(EconomyInvariantError, match="insufficient credits"):
        wallet.buy_offer(offer=active_offer(price=1))


def test_wallet_buy_offer_rejects_expired_offer() -> None:
    wallet, _, _ = create_wallet(PLAYER_ID).apply_match_result(
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )

    with pytest.raises(EconomyInvariantError, match="expired"):
        wallet.buy_offer(
            offer=active_offer(
                price=1,
                expires_at=datetime.now(UTC) - timedelta(days=1),
            )
        )


def test_shop_offer_rejects_invalid_price() -> None:
    with pytest.raises(EconomyInvariantError, match="price"):
        active_offer(price=0)


def active_offer(
    *,
    price: int,
    expires_at: datetime | None = None,
) -> ShopOffer:
    return ShopOffer(
        id=SHOP_OFFER_ID,
        card_id=CARD_ID,
        card_name="Capitao Nebula",
        family="cosmic",
        rarity=64,
        price=price,
        expires_at=expires_at or datetime.now(UTC) + timedelta(days=1),
    )
