from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.application.use_cases import (
    ApplyMatchResultCommand,
    ApplyMatchResultCredits,
    BuyShopOffer,
    BuyShopOfferCommand,
    GetWalletCredits,
    GetWalletCreditsQuery,
    ListShopOffers,
)
from app.domain.entities import (
    CreditLedgerEntry,
    InventoryCard,
    MatchResult,
    Purchase,
    ShopOffer,
    Wallet,
)
from app.domain.exceptions import (
    EconomyInvariantError,
    InsufficientCreditsError,
    ShopOfferExpiredError,
    ShopOfferNotFoundError,
    WalletNotFoundError,
)


class ApplyMatchResultCreditsRequest(BaseModel):
    player_id: UUID
    match_id: UUID
    result: MatchResult


class BuyShopOfferRequest(BaseModel):
    player_id: UUID
    offer_id: UUID


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


class ShopOfferResponse(BaseModel):
    id: str
    card_id: str
    card_name: str
    family: str
    rarity: int
    price: int
    expires_at: datetime


class ShopOffersResponse(BaseModel):
    service: str
    task: str
    offers: list[ShopOfferResponse]


class PurchaseResponse(BaseModel):
    id: str
    player_id: str
    offer_id: str
    card_id: str
    price: int
    purchased_at: datetime


class InventoryCardResponse(BaseModel):
    id: str
    player_id: str
    card_id: str
    source_offer_id: str
    acquired_at: datetime


class BuyShopOfferResponse(BaseModel):
    service: str
    task: str
    player_id: str
    balance: int
    offer: ShopOfferResponse
    purchase: PurchaseResponse
    inventory_card: InventoryCardResponse
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

    @router.get(
        "/shop/offers",
        operation_id="listShopOffers",
        response_model=ShopOffersResponse,
    )
    async def shop_offers(request: Request) -> ShopOffersResponse:
        result = ListShopOffers(request.app.state.shop_offer_repository).execute()

        return ShopOffersResponse(
            service="economy-service",
            task="ST-502",
            offers=[shop_offer_response(offer) for offer in result.offers],
        )

    @router.post(
        "/shop/buy",
        operation_id="buyShopOffer",
        response_model=BuyShopOfferResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            404: {"description": "Wallet or shop offer not found"},
            409: {"description": "Shop offer cannot be purchased"},
        },
    )
    async def buy_offer(
        payload: BuyShopOfferRequest,
        request: Request,
    ) -> BuyShopOfferResponse | JSONResponse:
        try:
            result = BuyShopOffer(
                request.app.state.wallet_repository,
                request.app.state.shop_offer_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                BuyShopOfferCommand(
                    player_id=payload.player_id,
                    offer_id=payload.offer_id,
                )
            )
        except WalletNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Wallet not found."},
            )
        except ShopOfferNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Shop offer not found."},
            )
        except ShopOfferExpiredError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Shop offer expired."},
            )
        except InsufficientCreditsError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Insufficient credits."},
            )
        except EconomyInvariantError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Request could not be processed."},
            )

        return BuyShopOfferResponse(
            service="economy-service",
            task="ST-502",
            player_id=str(result.wallet.player_id),
            balance=result.wallet.balance,
            offer=shop_offer_response(result.offer),
            purchase=purchase_response(result.purchase),
            inventory_card=inventory_card_response(result.inventory_card),
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


def shop_offer_response(offer: ShopOffer) -> ShopOfferResponse:
    return ShopOfferResponse(
        id=str(offer.id),
        card_id=str(offer.card_id),
        card_name=offer.card_name,
        family=offer.family,
        rarity=offer.rarity,
        price=offer.price,
        expires_at=offer.expires_at,
    )


def purchase_response(purchase: Purchase) -> PurchaseResponse:
    return PurchaseResponse(
        id=str(purchase.id),
        player_id=str(purchase.player_id),
        offer_id=str(purchase.offer_id),
        card_id=str(purchase.card_id),
        price=purchase.price,
        purchased_at=purchase.purchased_at,
    )


def inventory_card_response(inventory_card: InventoryCard) -> InventoryCardResponse:
    return InventoryCardResponse(
        id=str(inventory_card.id),
        player_id=str(inventory_card.player_id),
        card_id=str(inventory_card.card_id),
        source_offer_id=str(inventory_card.source_offer_id),
        acquired_at=inventory_card.acquired_at,
    )
