from dataclasses import dataclass
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import CreditLedgerEntry, MatchResult, Wallet, create_wallet
from app.domain.events import credits_earned_event
from app.domain.exceptions import WalletNotFoundError
from app.domain.repositories import DomainEventPublisher, WalletRepository


@dataclass(frozen=True)
class ApplyMatchResultCommand:
    player_id: UUID
    match_id: UUID
    result: MatchResult


@dataclass(frozen=True)
class ApplyMatchResultResult:
    wallet: Wallet
    ledger_entry: CreditLedgerEntry
    created: bool
    events: tuple[DomainEvent, ...]


@dataclass(frozen=True)
class GetWalletCreditsQuery:
    player_id: UUID


class ApplyMatchResultCredits:
    def __init__(
        self,
        repository: WalletRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: ApplyMatchResultCommand) -> ApplyMatchResultResult:
        wallet = self.repository.find_by_player_id(command.player_id) or create_wallet(
            command.player_id
        )
        updated_wallet, ledger_entry, created = wallet.apply_match_result(
            match_id=command.match_id,
            result=command.result,
        )
        self.repository.save(updated_wallet)

        events: tuple[DomainEvent, ...] = ()

        if created and ledger_entry.amount > 0:
            event = credits_earned_event(updated_wallet, ledger_entry)
            self.event_publisher.publish(event)
            events = (event,)

        return ApplyMatchResultResult(
            wallet=updated_wallet,
            ledger_entry=ledger_entry,
            created=created,
            events=events,
        )


class GetWalletCredits:
    def __init__(self, repository: WalletRepository) -> None:
        self.repository = repository

    def execute(self, query: GetWalletCreditsQuery) -> Wallet:
        wallet = self.repository.find_by_player_id(query.player_id)

        if wallet is None:
            raise WalletNotFoundError("wallet was not found")

        return wallet

