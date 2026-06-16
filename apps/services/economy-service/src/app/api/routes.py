from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.application.use_cases import (
    ApplyMatchResultCommand,
    ApplyMatchResultCredits,
    GetWalletCredits,
    GetWalletCreditsQuery,
)
from app.domain.entities import CreditLedgerEntry, MatchResult, Wallet
from app.domain.exceptions import WalletNotFoundError


class ApplyMatchResultCreditsRequest(BaseModel):
    player_id: UUID
    match_id: UUID
    result: MatchResult


class CreditLedgerEntryResponse(BaseModel):
    id: str
    player_id: str
    match_id: str
    amount: int
    reason: str
    created_at: datetime


class EconomyEventResponse(BaseModel):
    name: str
    aggregate_id: str
    payload: dict[str, object]
    occurred_at: datetime
    event_id: str


class WalletCreditsResponse(BaseModel):
    service: str
    task: str
    player_id: str
    balance: int
    ledger_entries: list[CreditLedgerEntryResponse]


class ApplyMatchResultCreditsResponse(WalletCreditsResponse):
    created: bool
    awarded_credits: int
    ledger_entry: CreditLedgerEntryResponse
    events: list[EconomyEventResponse]


def create_economy_router() -> APIRouter:
    router = APIRouter(tags=["economy"])

    @router.get(
        "/wallet/credits",
        operation_id="getWalletCredits",
        response_model=WalletCreditsResponse,
        responses={404: {"description": "Wallet not found"}},
    )
    async def wallet_credits(
        request: Request,
        player_id: Annotated[UUID, Query()],
    ) -> WalletCreditsResponse | JSONResponse:
        use_case = GetWalletCredits(request.app.state.wallet_repository)

        try:
            wallet = use_case.execute(GetWalletCreditsQuery(player_id=player_id))
        except WalletNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Wallet not found."},
            )

        return wallet_response(wallet)

    @router.post(
        "/wallet/credits/match-result",
        operation_id="applyMatchResultCredits",
        response_model=ApplyMatchResultCreditsResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def apply_match_result_credits(
        payload: ApplyMatchResultCreditsRequest,
        request: Request,
    ) -> ApplyMatchResultCreditsResponse:
        result = ApplyMatchResultCredits(
            request.app.state.wallet_repository,
            request.app.state.domain_event_publisher,
        ).execute(
            ApplyMatchResultCommand(
                player_id=payload.player_id,
                match_id=payload.match_id,
                result=payload.result,
            )
        )

        return ApplyMatchResultCreditsResponse(
            **wallet_response(result.wallet).model_dump(),
            created=result.created,
            awarded_credits=result.ledger_entry.amount,
            ledger_entry=ledger_entry_response(result.ledger_entry),
            events=[
                EconomyEventResponse(
                    name=event.name,
                    aggregate_id=event.aggregate_id,
                    payload=event.payload,
                    occurred_at=event.occurred_at,
                    event_id=event.event_id,
                )
                for event in result.events
            ],
        )

    @router.get("/shop/offers", status_code=status.HTTP_202_ACCEPTED)
    async def shop_offers() -> dict[str, str]:
        return {"service": "economy-service", "status": "planned", "task": "ST-502"}

    @router.post("/shop/buy", status_code=status.HTTP_202_ACCEPTED)
    async def buy_offer() -> dict[str, str]:
        return {"service": "economy-service", "status": "planned", "task": "ST-502"}

    return router


def wallet_response(wallet: Wallet) -> WalletCreditsResponse:
    return WalletCreditsResponse(
        service="economy-service",
        task="ST-501",
        player_id=str(wallet.player_id),
        balance=wallet.balance,
        ledger_entries=[ledger_entry_response(entry) for entry in wallet.ledger_entries],
    )


def ledger_entry_response(entry: CreditLedgerEntry) -> CreditLedgerEntryResponse:
    return CreditLedgerEntryResponse(
        id=str(entry.id),
        player_id=str(entry.player_id),
        match_id=str(entry.match_id),
        amount=entry.amount,
        reason=entry.reason.value,
        created_at=entry.created_at,
    )
