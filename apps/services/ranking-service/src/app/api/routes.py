from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from super_trunfo_shared import DomainEvent

from app.application.use_cases import (
    RecalculatePlayerRating,
    RecalculatePlayerRatingCommand,
)
from app.domain.entities import Rating
from app.domain.exceptions import RankingInvariantError


class RecalculatePlayerRatingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    match_id: UUID
    winner_id: UUID
    loser_id: UUID


class RatingResponse(BaseModel):
    player_id: str
    score: int
    tier: str
    matches_played: int
    wins: int
    losses: int
    updated_at: datetime | None


class RankingEventResponse(BaseModel):
    name: str
    aggregate_id: str
    payload: dict[str, object]
    occurred_at: datetime
    event_id: str


class RecalculatePlayerRatingResponse(BaseModel):
    service: str
    task: str
    match_id: str
    created: bool
    winner: RatingResponse
    loser: RatingResponse
    events: list[RankingEventResponse]


def create_ranking_router() -> APIRouter:
    router = APIRouter(tags=["ranking"])

    @router.get("/ranking/global", status_code=status.HTTP_202_ACCEPTED)
    async def global_ranking() -> dict[str, str]:
        return {"service": "ranking-service", "status": "planned", "task": "ST-504"}

    @router.get("/ranking/friends", status_code=status.HTTP_202_ACCEPTED)
    async def friends_ranking() -> dict[str, str]:
        return {"service": "ranking-service", "status": "planned", "task": "ST-504"}

    @router.post(
        "/ranking/recalculate",
        operation_id="recalculatePlayerRating",
        response_model=RecalculatePlayerRatingResponse,
        status_code=status.HTTP_201_CREATED,
        responses={400: {"description": "Invalid ranking recalculation"}},
    )
    async def recalculate_ranking(
        payload: RecalculatePlayerRatingRequest,
        request: Request,
    ) -> RecalculatePlayerRatingResponse | JSONResponse:
        try:
            result = RecalculatePlayerRating(
                request.app.state.rating_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                RecalculatePlayerRatingCommand(
                    match_id=payload.match_id,
                    winner_id=payload.winner_id,
                    loser_id=payload.loser_id,
                )
            )
        except RankingInvariantError as exc:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)},
            )

        return RecalculatePlayerRatingResponse(
            service="ranking-service",
            task="ST-503",
            match_id=str(payload.match_id),
            created=result.created,
            winner=rating_response(result.winner_rating),
            loser=rating_response(result.loser_rating),
            events=ranking_event_responses(result.events),
        )

    return router


def rating_response(rating: Rating) -> RatingResponse:
    return RatingResponse(
        player_id=str(rating.player_id),
        score=rating.score,
        tier=rating.tier.value,
        matches_played=rating.matches_played,
        wins=rating.wins,
        losses=rating.losses,
        updated_at=rating.updated_at,
    )


def ranking_event_responses(
    events: tuple[DomainEvent, ...],
) -> list[RankingEventResponse]:
    return [ranking_event_response(event) for event in events]


def ranking_event_response(event: DomainEvent) -> RankingEventResponse:
    payload = {
        "name": event.name,
        "aggregate_id": event.aggregate_id,
        "payload": event.payload,
        "occurred_at": event.occurred_at,
        "event_id": event.event_id,
    }

    return RankingEventResponse(**payload)
