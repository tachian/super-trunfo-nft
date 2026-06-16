from dataclasses import dataclass

from .entities import CreditLedgerReason, Wallet

ABUSE_BALANCE_THRESHOLD = 20
ABUSE_PURCHASE_THRESHOLD = 10
ABUSE_WIN_STREAK_THRESHOLD = 5


@dataclass(frozen=True)
class EconomicTelemetrySnapshot:
    wallet_count: int
    total_credits_earned: int
    total_credits_spent: int
    total_purchases: int
    average_balance: float
    max_balance: int
    economy_supply: int
    highest_win_streak: int
    abuse_signal_count: int
    inflation_status: str


def economic_telemetry_snapshot(
    wallets: tuple[Wallet, ...],
) -> EconomicTelemetrySnapshot:
    wallet_count = len(wallets)
    total_credits_earned = sum(
        entry.amount for wallet in wallets for entry in wallet.ledger_entries
    )
    total_credits_spent = sum(
        purchase.price for wallet in wallets for purchase in wallet.purchases
    )
    total_purchases = sum(len(wallet.purchases) for wallet in wallets)
    economy_supply = sum(wallet.balance for wallet in wallets)
    max_balance = max((wallet.balance for wallet in wallets), default=0)
    average_balance = round(economy_supply / wallet_count, 2) if wallet_count else 0.0
    win_streaks = tuple(current_win_streak(wallet) for wallet in wallets)
    highest_win_streak = max(win_streaks, default=0)
    abuse_signal_count = sum(1 for wallet in wallets if has_abuse_signal(wallet))

    return EconomicTelemetrySnapshot(
        wallet_count=wallet_count,
        total_credits_earned=total_credits_earned,
        total_credits_spent=total_credits_spent,
        total_purchases=total_purchases,
        average_balance=average_balance,
        max_balance=max_balance,
        economy_supply=economy_supply,
        highest_win_streak=highest_win_streak,
        abuse_signal_count=abuse_signal_count,
        inflation_status=inflation_status(
            total_credits_earned=total_credits_earned,
            total_credits_spent=total_credits_spent,
            average_balance=average_balance,
        ),
    )


def current_win_streak(wallet: Wallet) -> int:
    streak = 0

    for entry in sorted(wallet.ledger_entries, key=lambda ledger: ledger.created_at):
        if entry.reason == CreditLedgerReason.MATCH_VICTORY and entry.amount > 0:
            streak += 1
            continue

        streak = 0

    return streak


def has_abuse_signal(wallet: Wallet) -> bool:
    return (
        wallet.balance >= ABUSE_BALANCE_THRESHOLD
        or len(wallet.purchases) >= ABUSE_PURCHASE_THRESHOLD
        or current_win_streak(wallet) >= ABUSE_WIN_STREAK_THRESHOLD
    )


def inflation_status(
    *,
    total_credits_earned: int,
    total_credits_spent: int,
    average_balance: float,
) -> str:
    if total_credits_earned == 0:
        return "stable"

    spent_ratio = total_credits_spent / total_credits_earned

    if average_balance >= 20 or spent_ratio < 0.2:
        return "critical"

    if average_balance >= 5 or spent_ratio < 0.5:
        return "watch"

    return "stable"
