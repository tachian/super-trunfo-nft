from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.application.use_cases import GetEconomicTelemetry
from app.domain.entities import MatchResult, ShopOffer, Wallet, create_wallet
from app.domain.telemetry import current_win_streak, economic_telemetry_snapshot
from app.infrastructure.repositories import InMemoryWalletRepository

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000505")
SECOND_PLAYER_ID = UUID("22222222-2222-4222-8222-000000000505")
OFFER_ID = UUID("33333333-3333-4333-8333-000000000505")
CARD_ID = UUID("44444444-4444-4444-8444-000000000505")


def test_current_win_streak_resets_after_defeat() -> None:
    wallet = wallet_with_results(
        PLAYER_ID,
        (
            MatchResult.VICTORY,
            MatchResult.VICTORY,
            MatchResult.DEFEAT,
            MatchResult.VICTORY,
        ),
    )

    assert current_win_streak(wallet) == 1


def test_economic_telemetry_snapshot_tracks_spend_balance_and_abuse() -> None:
    wallet = wallet_with_results(PLAYER_ID, (MatchResult.VICTORY,) * 5)
    second_wallet = wallet_with_results(SECOND_PLAYER_ID, (MatchResult.VICTORY,) * 2)
    second_wallet, _, _ = second_wallet.buy_offer(offer=shop_offer(price=1))

    snapshot = economic_telemetry_snapshot((wallet, second_wallet))

    assert snapshot.wallet_count == 2
    assert snapshot.total_credits_earned == 7
    assert snapshot.total_credits_spent == 1
    assert snapshot.total_purchases == 1
    assert snapshot.economy_supply == 6
    assert snapshot.average_balance == 3
    assert snapshot.max_balance == 5
    assert snapshot.highest_win_streak == 5
    assert snapshot.abuse_signal_count == 1
    assert snapshot.inflation_status == "critical"


def test_get_economic_telemetry_reads_wallet_repository() -> None:
    repository = InMemoryWalletRepository()
    repository.save(wallet_with_results(PLAYER_ID, (MatchResult.VICTORY,)))

    result = GetEconomicTelemetry(repository).execute()

    assert result.snapshot.wallet_count == 1
    assert result.snapshot.total_credits_earned == 1
    assert result.snapshot.inflation_status == "critical"


def wallet_with_results(
    player_id: UUID,
    results: tuple[MatchResult, ...],
) -> Wallet:
    wallet = create_wallet(player_id)
    created_at = datetime(2026, 6, 16, tzinfo=UTC)

    for index, result in enumerate(results, start=1):
        wallet, _, _ = wallet.apply_match_result(
            match_id=UUID(f"55555555-5555-4555-8555-{index:012d}"),
            result=result,
            created_at=created_at + timedelta(minutes=index),
        )

    return wallet


def shop_offer(*, price: int) -> ShopOffer:
    return ShopOffer(
        id=OFFER_ID,
        card_id=CARD_ID,
        card_name="Telemetria Card",
        family="metrics",
        rarity=50,
        price=price,
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
