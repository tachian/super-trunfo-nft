from uuid import UUID

import pytest
from app.application.use_cases import (
    ApplyMatchResultCommand,
    ApplyMatchResultCredits,
    GetWalletCredits,
    GetWalletCreditsQuery,
)
from app.domain.entities import MatchResult
from app.domain.exceptions import WalletNotFoundError
from app.infrastructure.repositories import InMemoryWalletRepository
from super_trunfo_shared import InMemoryDomainEventPublisher

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000501")
MATCH_ID = UUID("22222222-2222-4222-8222-000000000501")


def test_apply_match_victory_persists_credit_and_event() -> None:
    repository = InMemoryWalletRepository()
    publisher = InMemoryDomainEventPublisher(service_name="economy-service", context="economy")

    result = ApplyMatchResultCredits(repository, publisher).execute(
        ApplyMatchResultCommand(
            player_id=PLAYER_ID,
            match_id=MATCH_ID,
            result=MatchResult.VICTORY,
        )
    )

    assert result.created is True
    assert result.ledger_entry.amount == 1
    assert result.wallet.balance == 1
    assert repository.find_by_player_id(PLAYER_ID) == result.wallet
    assert len(result.events) == 1
    assert result.events[0].name == "CreditsEarned"
    assert publisher.published_events()[0].payload["amount"] == 1


def test_apply_match_defeat_persists_zero_credit_without_event() -> None:
    repository = InMemoryWalletRepository()
    publisher = InMemoryDomainEventPublisher(service_name="economy-service", context="economy")

    result = ApplyMatchResultCredits(repository, publisher).execute(
        ApplyMatchResultCommand(
            player_id=PLAYER_ID,
            match_id=MATCH_ID,
            result=MatchResult.DEFEAT,
        )
    )

    assert result.created is True
    assert result.ledger_entry.amount == 0
    assert result.wallet.balance == 0
    assert result.events == ()
    assert publisher.published_events() == ()


def test_apply_match_result_is_idempotent() -> None:
    repository = InMemoryWalletRepository()
    publisher = InMemoryDomainEventPublisher(service_name="economy-service", context="economy")
    use_case = ApplyMatchResultCredits(repository, publisher)
    command = ApplyMatchResultCommand(
        player_id=PLAYER_ID,
        match_id=MATCH_ID,
        result=MatchResult.VICTORY,
    )

    first = use_case.execute(command)
    second = use_case.execute(command)

    assert first.created is True
    assert second.created is False
    assert second.wallet.balance == 1
    assert second.ledger_entry == first.ledger_entry
    assert len(publisher.published_events()) == 1


def test_get_wallet_credits_rejects_missing_wallet() -> None:
    with pytest.raises(WalletNotFoundError, match="not found"):
        GetWalletCredits(InMemoryWalletRepository()).execute(
            GetWalletCreditsQuery(player_id=PLAYER_ID)
        )

