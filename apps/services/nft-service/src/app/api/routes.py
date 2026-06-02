from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from app.application.use_cases import (
    GenerateNftMetadata,
    GenerateNftMetadataCommand,
    GetNftMetadata,
    GetNftMetadataQuery,
)
from app.domain.entities import NftMetadata
from app.domain.exceptions import NftMetadataNotFoundError


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
    async def mint_nft() -> dict[str, str]:
        return {
            "service": "nft-service",
            "status": "disabled",
            "task": "ST-701",
            "reason": "Mint on-chain is outside the MVP scope.",
        }

    @router.get("/marketplace/listings", status_code=status.HTTP_202_ACCEPTED, tags=["marketplace"])
    async def marketplace_listings() -> dict[str, str]:
        return {"service": "nft-service", "status": "planned", "task": "ST-703"}

    return router


def metadata_response(metadata: NftMetadata) -> NftMetadataResponse:
    erc721_metadata = metadata.to_erc721_json()

    return NftMetadataResponse.model_validate(erc721_metadata)
