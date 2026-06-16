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
class Wallet:
    player_id: UUID
    balance: int
    ledger_entries: tuple[CreditLedgerEntry, ...] = ()

    def __post_init__(self) -> None:
        if self.balance < 0:
            raise EconomyInvariantError("wallet balance cannot be negative")

        if any(entry.player_id != self.player_id for entry in self.ledger_entries):
            raise EconomyInvariantError("wallet ledger entry must belong to wallet player")

        ledger_total = sum(entry.amount for entry in self.ledger_entries)

        if ledger_total != self.balance:
            raise EconomyInvariantError("wallet balance must match ledger total")

        match_ids = [entry.match_id for entry in self.ledger_entries]

        if len(match_ids) != len(set(match_ids)):
            raise EconomyInvariantError("wallet ledger cannot contain duplicated match result")

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
            ),
            entry,
            True,
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

