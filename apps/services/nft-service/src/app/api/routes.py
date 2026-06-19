from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.application.use_cases import (
    CreateMarketplaceListing,
    CreateMarketplaceListingCommand,
    GenerateNftMetadata,
    GenerateNftMetadataCommand,
    GetNftMetadata,
    GetNftMetadataQuery,
    ListMarketplaceListings,
)
from app.domain.entities import MarketplaceListing, NftMetadata
from app.domain.exceptions import NftInvariantError, NftMetadataNotFoundError


class GenerateNftMetadataRequest(BaseModel):
    card_id: UUID
    name: Annotated[str, Field(min_length=1, max_length=120)]
    family: Annotated[str, Field(min_length=1, max_length=50)]
    rarity: Annotated[int, Field(ge=0, le=100)]
    level: Annotated[int, Field(ge=0)]
    speed: Annotated[int | None, Field(ge=0, le=100)] = None
    strength: Annotated[int | None, Field(ge=0, le=100)] = None
    intelligence: Annotated[int | None, Field(ge=0, le=100)] = None
    resistance: Annotated[int | None, Field(ge=0, le=100)] = None
    expires_at: datetime | None = None

    @field_validator("name", "family")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("value cannot be blank")

        return normalized


class NftAttributeResponse(BaseModel):
    trait_type: str
    value: int | str


class NftMetadataPropertiesResponse(BaseModel):
    card_id: str
    metadata_uri: str
    generated_at: datetime
    mint_enabled: bool


class NftMetadataResponse(BaseModel):
    name: str
    description: str
    image: str
    attributes: list[NftAttributeResponse]
    properties: NftMetadataPropertiesResponse


class CreateMarketplaceListingRequest(BaseModel):
    seller_id: UUID
    card_id: UUID
    token_id: Annotated[int, Field(gt=0)]
    price: Annotated[int, Field(gt=0)]
    expires_at: datetime


class MarketplaceListingHistoryResponse(BaseModel):
    status: str
    changed_at: datetime
    reason: str


class MarketplaceListingResponse(BaseModel):
    id: UUID
    seller_id: UUID
    card_id: UUID
    token_id: int
    price: int
    status: str
    expires_at: datetime
    created_at: datetime
    history: list[MarketplaceListingHistoryResponse]


def create_nft_router() -> APIRouter:
    router = APIRouter(tags=["nft"])

    @router.post(
        "/nft/metadata/offline",
        status_code=status.HTTP_201_CREATED,
        response_model=NftMetadataResponse,
    )
    async def generate_offline_metadata(
        payload: GenerateNftMetadataRequest,
        request: Request,
    ) -> NftMetadataResponse:
        use_case = GenerateNftMetadata(
            request.app.state.nft_metadata_repository,
            request.app.state.domain_event_publisher,
        )
        metadata = use_case.execute(
            GenerateNftMetadataCommand(
                card_id=payload.card_id,
                card_name=payload.name,
                family=payload.family,
                rarity=payload.rarity,
                level=payload.level,
                speed=payload.speed,
                strength=payload.strength,
                intelligence=payload.intelligence,
                resistance=payload.resistance,
                expires_at=payload.expires_at,
                mint_enabled=request.app.state.nft_feature_flags.blockchain_enabled,
            )
        )

        return metadata_response(metadata)

    @router.get(
        "/nft/metadata/{card_id}",
        response_model=NftMetadataResponse,
        responses={404: {"description": "Offline NFT metadata not found"}},
    )
    async def get_nft_metadata(
        card_id: UUID,
        request: Request,
    ) -> NftMetadataResponse | JSONResponse:
        use_case = GetNftMetadata(request.app.state.nft_metadata_repository)

        try:
            metadata = use_case.execute(GetNftMetadataQuery(card_id=card_id))
        except NftMetadataNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Offline NFT metadata not found."},
            )

        return metadata_response(metadata)

    @router.post("/nft/mint", status_code=status.HTTP_202_ACCEPTED)
    async def mint_nft(request: Request) -> dict[str, object]:
        blockchain_enabled = request.app.state.nft_feature_flags.blockchain_enabled

        if blockchain_enabled:
            return {
                "service": "nft-service",
                "status": "enabled",
                "task": "ST-705",
                "feature_nft_enabled": True,
                "reason": "Blockchain feature flag is enabled for post-MVP mint flows.",
            }

        return {
            "service": "nft-service",
            "status": "disabled",
            "task": "ST-705",
            "feature_nft_enabled": False,
            "reason": "Blockchain features are disabled by default for the MVP.",
        }

    @router.post(
        "/marketplace/listings",
        status_code=status.HTTP_201_CREATED,
        response_model=MarketplaceListingResponse,
        tags=["marketplace"],
        responses={400: {"description": "Invalid marketplace listing"}},
    )
    async def create_marketplace_listing(
        payload: CreateMarketplaceListingRequest,
        request: Request,
    ) -> MarketplaceListingResponse | JSONResponse:
        use_case = CreateMarketplaceListing(
            request.app.state.marketplace_listing_repository,
            request.app.state.domain_event_publisher,
        )

        try:
            result = use_case.execute(
                CreateMarketplaceListingCommand(
                    seller_id=payload.seller_id,
                    card_id=payload.card_id,
                    token_id=payload.token_id,
                    price=payload.price,
                    expires_at=payload.expires_at,
                )
            )
        except NftInvariantError as _exc:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid marketplace listing."},
            )

        return marketplace_listing_response(result.listing)

    @router.get(
        "/marketplace/listings",
        response_model=list[MarketplaceListingResponse],
        tags=["marketplace"],
    )
    async def marketplace_listings(request: Request) -> list[MarketplaceListingResponse]:
        use_case = ListMarketplaceListings(request.app.state.marketplace_listing_repository)
        result = use_case.execute()

        return [marketplace_listing_response(listing) for listing in result.listings]

    return router


def metadata_response(metadata: NftMetadata) -> NftMetadataResponse:
    erc721_metadata = metadata.to_erc721_json()

    return NftMetadataResponse.model_validate(erc721_metadata)


def marketplace_listing_response(listing: MarketplaceListing) -> MarketplaceListingResponse:
    return MarketplaceListingResponse(
        id=listing.id,
        seller_id=listing.seller_id,
        card_id=listing.card_id,
        token_id=listing.token_id,
        price=listing.price,
        status=listing.status.value,
        expires_at=listing.expires_at,
        created_at=listing.created_at,
        history=[
            MarketplaceListingHistoryResponse(
                status=entry.status.value,
                changed_at=entry.changed_at,
                reason=entry.reason,
            )
            for entry in listing.history
        ],
    )
