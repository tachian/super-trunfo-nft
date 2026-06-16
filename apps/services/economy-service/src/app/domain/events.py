from super_trunfo_shared import DomainEvent

from .entities import CreditLedgerEntry, Wallet


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

