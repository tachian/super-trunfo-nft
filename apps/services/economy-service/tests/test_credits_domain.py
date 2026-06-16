from uuid import UUID

import pytest
from app.domain.entities import (
    CreditLedgerEntry,
    CreditLedgerReason,
    MatchResult,
    Wallet,
    create_wallet,
    credits_for_match_result,
)
from app.domain.exceptions import EconomyInvariantError

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000501")
MATCH_ID = UUID("22222222-2222-4222-8222-000000000501")


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

