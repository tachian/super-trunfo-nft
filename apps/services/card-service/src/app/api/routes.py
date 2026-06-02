from datetime import datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from super_trunfo_shared.cards import CardAttributes, card_uniqueness_hash

from app.application.use_cases import (
    GenerateUniqueCard,
    GenerateUniqueCardCommand,
    GenerateUniqueCardResult,
)
from app.domain.entities import Card, create_card
from app.domain.exceptions import DuplicateCardGenerationError


class CardResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    family: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int
    level: int
    uniqueness_hash: str
    created_at: datetime
    expires_at: datetime


class GenerateSampleCardRequest(BaseModel):
    owner_id: UUID = UUID("11111111-1111-4111-8111-111111111111")
    family: str = Field(default="shadow", min_length=1, max_length=50)


class GenerateSampleCardResponse(BaseModel):
    card: CardResponse
    attempts: int


def create_cards_router() -> APIRouter:
    router = APIRouter(tags=["cards"])

    @router.get("/cards", status_code=status.HTTP_202_ACCEPTED)
    async def list_cards() -> dict[str, str]:
        return {"service": "card-service", "status": "planned", "task": "ST-201"}

    @router.post("/cards/select-deck", status_code=status.HTTP_202_ACCEPTED)
    async def select_deck() -> dict[str, str]:
        return {"service": "card-service", "status": "planned", "task": "ST-301"}

    @router.get("/cards/sample/model", response_model=CardResponse)
    async def sample_card_model() -> CardResponse:
        attributes = sample_attributes()
        card = create_card(
            owner_id=UUID("11111111-1111-4111-8111-111111111111"),
            attributes=attributes,
            family="shadow",
            card_id=UUID("22222222-2222-4222-8222-222222222222"),
        )

        return card_response(card)

    @router.get("/cards/sample/hash")
    async def sample_card_hash() -> dict[str, object]:
        attributes = sample_attributes()

        return {
            "level": create_card(
                owner_id=uuid4(),
                attributes=attributes,
                family="shadow",
            ).level,
            "hash": card_uniqueness_hash(attributes),
        }

    @router.post(
        "/cards/sample/generate",
        status_code=status.HTTP_201_CREATED,
        response_model=GenerateSampleCardResponse,
        responses={409: {"description": "Unable to generate a unique card"}},
    )
    async def generate_sample_card(
        payload: GenerateSampleCardRequest,
        request: Request,
    ) -> GenerateSampleCardResponse | JSONResponse:
        use_case = GenerateUniqueCard(
            request.app.state.card_repository,
            request.app.state.card_attribute_generator,
        )

        try:
            result = use_case.execute(
                GenerateUniqueCardCommand(
                    owner_id=payload.owner_id,
                    family=payload.family,
                )
            )
        except DuplicateCardGenerationError:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={"detail": "Unable to generate a unique card."},
            )

        return generated_card_response(result)

    @router.get("/cards/{card_id}", status_code=status.HTTP_202_ACCEPTED)
    async def get_card(card_id: str) -> dict[str, str]:
        return {
            "service": "card-service",
            "card_id": card_id,
            "status": "planned",
            "task": "ST-201",
        }

    return router


def sample_attributes() -> CardAttributes:
    return CardAttributes(
        name="Shadow Titan",
        speed=82,
        strength=91,
        intelligence=64,
        resistance=76,
        rarity=80,
    )


def card_response(card: Card) -> CardResponse:
    return CardResponse(
        id=str(card.id),
        owner_id=str(card.owner_id),
        name=card.name,
        family=card.family,
        speed=card.speed,
        strength=card.strength,
        intelligence=card.intelligence,
        resistance=card.resistance,
        rarity=card.rarity,
        level=card.level,
        uniqueness_hash=card.uniqueness_hash,
        created_at=card.created_at,
        expires_at=card.expires_at,
    )


def generated_card_response(result: GenerateUniqueCardResult) -> GenerateSampleCardResponse:
    return GenerateSampleCardResponse(
        card=card_response(result.card),
        attempts=result.attempts,
    )
