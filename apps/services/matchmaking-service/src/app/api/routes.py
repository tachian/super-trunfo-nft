from uuid import UUID

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

from app.application.use_cases import GetQueueStatus, RequestMatch, RequestMatchCommand
from app.domain.entities import (
    MatchmakingMatch,
    MatchmakingOpponent,
    MatchmakingTicket,
    MatchStartedEvent,
)
from app.domain.repositories import QueueStatus


class MatchmakingQueueResponse(BaseModel):
    tier: str
    name: str
    size: int


class MatchmakingQueuesResponse(BaseModel):
    service: str
    task: str
    backend: str
    queues: list[MatchmakingQueueResponse]


class FindMatchRequest(BaseModel):
    player_id: UUID
    average_deck_level: int = Field(ge=0)
    fallback_after_seconds: int = Field(default=0, ge=0)


class MatchmakingTicketResponse(BaseModel):
    id: str
    player_id: str
    average_deck_level: int
    tier: str
    queue: str


class MatchmakingOpponentResponse(BaseModel):
    id: str
    kind: str
    average_deck_level: int
    tier: str
    ticket_id: str | None = None


class MatchmakingMatchResponse(BaseModel):
    id: str
    mode: str
    opponent: MatchmakingOpponentResponse


class MatchmakingEventResponse(BaseModel):
    name: str
    schema_version: str
    match_id: str
    mode: str
    player_id: str
    opponent_id: str
    opponent_kind: str
    player_average_deck_level: int
    opponent_average_deck_level: int
    occurred_at: str


class FindMatchResponse(BaseModel):
    service: str
    task: str
    status: str
    tolerance: int
    fallback_after_seconds: int
    ticket: MatchmakingTicketResponse
    matched_ticket: MatchmakingTicketResponse | None = None
    match: MatchmakingMatchResponse | None = None
    events: list[MatchmakingEventResponse]


def create_matchmaking_router() -> APIRouter:
    router = APIRouter(tags=["matchmaking"])

    @router.post(
        "/matchmaking/find",
        operation_id="findMatch",
        response_model=FindMatchResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def find_match(payload: FindMatchRequest, request: Request) -> FindMatchResponse:
        result = RequestMatch(
            request.app.state.matchmaking_queue_repository,
            request.app.state.matchmaking_event_publisher,
        ).execute(
            RequestMatchCommand(
                player_id=payload.player_id,
                average_deck_level=payload.average_deck_level,
                fallback_after_seconds=payload.fallback_after_seconds,
            )
        )

        return FindMatchResponse(
            service="matchmaking-service",
            task="ST-403",
            status=result.status,
            tolerance=result.tolerance,
            fallback_after_seconds=result.fallback_after_seconds,
            ticket=ticket_response(result.ticket),
            matched_ticket=(
                ticket_response(result.matched_ticket)
                if result.matched_ticket is not None
                else None
            ),
            match=match_response(result.match) if result.match is not None else None,
            events=[event_response(event) for event in result.events],
        )

    @router.get(
        "/matchmaking/queues",
        operation_id="getMatchmakingQueues",
        response_model=MatchmakingQueuesResponse,
    )
    async def matchmaking_queues(request: Request) -> MatchmakingQueuesResponse:
        result = GetQueueStatus(request.app.state.matchmaking_queue_repository).execute()

        return MatchmakingQueuesResponse(
            service="matchmaking-service",
            task="ST-401",
            backend="redis",
            queues=[queue_response(status_item) for status_item in result.queues],
        )

    return router


def queue_response(status_item: QueueStatus) -> MatchmakingQueueResponse:
    return MatchmakingQueueResponse(
        tier=status_item.queue.tier.value,
        name=status_item.queue.name,
        size=status_item.size,
    )


def ticket_response(ticket: MatchmakingTicket) -> MatchmakingTicketResponse:
    return MatchmakingTicketResponse(
        id=str(ticket.id),
        player_id=str(ticket.player_id),
        average_deck_level=ticket.average_deck_level,
        tier=ticket.tier.value,
        queue=f"queue:{ticket.tier.value}",
    )


def opponent_response(opponent: MatchmakingOpponent) -> MatchmakingOpponentResponse:
    return MatchmakingOpponentResponse(
        id=str(opponent.id),
        kind=opponent.kind.value,
        average_deck_level=opponent.average_deck_level,
        tier=opponent.tier.value,
        ticket_id=str(opponent.ticket_id) if opponent.ticket_id is not None else None,
    )


def match_response(match: MatchmakingMatch) -> MatchmakingMatchResponse:
    return MatchmakingMatchResponse(
        id=str(match.id),
        mode=match.mode.value,
        opponent=opponent_response(match.opponent),
    )


def event_response(event: MatchStartedEvent) -> MatchmakingEventResponse:
    return MatchmakingEventResponse(
        name=event.name,
        schema_version=event.schema_version,
        match_id=str(event.match_id),
        mode=event.mode.value,
        player_id=str(event.player_id),
        opponent_id=str(event.opponent_id),
        opponent_kind=event.opponent_kind.value,
        player_average_deck_level=event.player_average_deck_level,
        opponent_average_deck_level=event.opponent_average_deck_level,
        occurred_at=event.occurred_at.isoformat(),
    )
