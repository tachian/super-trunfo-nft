from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from app.application.use_cases import (
    ApplyMatchResultCommand,
    ApplyMatchResultCredits,
    BuyShopOffer,
    BuyShopOfferCommand,
    GetWalletCredits,
    GetWalletCreditsQuery,
    ListShopOffers,
)
from app.domain.entities import MatchResult, ShopOffer
from app.domain.exceptions import InsufficientCreditsError, WalletNotFoundError
from app.infrastructure.repositories import (
    InMemoryShopOfferRepository,
    InMemoryWalletRepository,
)
from super_trunfo_shared import InMemoryDomainEventPublisher

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000501")
MATCH_ID = UUID("22222222-2222-4222-8222-000000000501")
SHOP_OFFER_ID = UUID("11111111-5020-4502-8502-000000000001")
CARD_ID = UUID("22222222-5020-4502-8502-000000000001")


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


def test_list_shop_offers_returns_only_active_offers() -> None:
    repository = InMemoryShopOfferRepository(
        offers=(
            shop_offer(SHOP_OFFER_ID, price=1),
            shop_offer(
                UUID("11111111-5020-4502-8502-000000000099"),
                price=1,
                expires_at=datetime.now(UTC) - timedelta(days=1),
            ),
        )
    )

    result = ListShopOffers(repository).execute()

    assert [offer.id for offer in result.offers] == [SHOP_OFFER_ID]


def test_buy_shop_offer_persists_purchase_and_publishes_event() -> None:
    wallet_repository = InMemoryWalletRepository()
    shop_offer_repository = InMemoryShopOfferRepository(
        offers=(shop_offer(SHOP_OFFER_ID, price=1),)
    )
    publisher = InMemoryDomainEventPublisher(service_name="economy-service", context="economy")
    wallet = ApplyMatchResultCredits(wallet_repository, publisher).execute(
        ApplyMatchResultCommand(
            player_id=PLAYER_ID,
            match_id=MATCH_ID,
            result=MatchResult.VICTORY,
        )
    ).wallet

    result = BuyShopOffer(
        wallet_repository,
        shop_offer_repository,
        publisher,
    ).execute(BuyShopOfferCommand(player_id=wallet.player_id, offer_id=SHOP_OFFER_ID))

    persisted_wallet = wallet_repository.find_by_player_id(PLAYER_ID)

    assert result.wallet.balance == 0
    assert result.purchase.price == 1
    assert result.inventory_card.card_id == CARD_ID
    assert persisted_wallet == result.wallet
    assert result.events[0].name == "OfferPurchased"
    assert publisher.published_events()[1].name == "OfferPurchased"


def test_buy_shop_offer_rejects_insufficient_credits() -> None:
    wallet_repository = InMemoryWalletRepository()
    shop_offer_repository = InMemoryShopOfferRepository(
        offers=(shop_offer(SHOP_OFFER_ID, price=2),)
    )
    publisher = InMemoryDomainEventPublisher(service_name="economy-service", context="economy")
    ApplyMatchResultCredits(wallet_repository, publisher).execute(
        ApplyMatchResultCommand(
            player_id=PLAYER_ID,
            match_id=MATCH_ID,
            result=MatchResult.VICTORY,
        )
    )

    with pytest.raises(InsufficientCreditsError, match="insufficient"):
        BuyShopOffer(
            wallet_repository,
            shop_offer_repository,
            publisher,
        ).execute(BuyShopOfferCommand(player_id=PLAYER_ID, offer_id=SHOP_OFFER_ID))


def shop_offer(
    offer_id: UUID,
    *,
    price: int,
    expires_at: datetime | None = None,
) -> ShopOffer:
    return ShopOffer(
        id=offer_id,
        card_id=CARD_ID,
        card_name="Capitao Nebula",
        family="cosmic",
        rarity=64,
        price=price,
        expires_at=expires_at or datetime.now(UTC) + timedelta(days=1),
    )
