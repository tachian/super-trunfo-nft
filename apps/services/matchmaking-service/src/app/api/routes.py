from uuid import UUID

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field

from app.application.use_cases import GetQueueStatus, RequestMatch, RequestMatchCommand
from app.domain.entities import MatchmakingTicket
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


class MatchmakingTicketResponse(BaseModel):
    id: str
    player_id: str
    average_deck_level: int
    tier: str
    queue: str


class FindMatchResponse(BaseModel):
    service: str
    task: str
    status: str
    tolerance: int
    ticket: MatchmakingTicketResponse
    matched_ticket: MatchmakingTicketResponse | None = None


def create_matchmaking_router() -> APIRouter:
    router = APIRouter(tags=["matchmaking"])

    @router.post(
        "/matchmaking/find",
        operation_id="findMatch",
        response_model=FindMatchResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def find_match(payload: FindMatchRequest, request: Request) -> FindMatchResponse:
        result = RequestMatch(request.app.state.matchmaking_queue_repository).execute(
            RequestMatchCommand(
                player_id=payload.player_id,
                average_deck_level=payload.average_deck_level,
            )
        )

        return FindMatchResponse(
            service="matchmaking-service",
            task="ST-402",
            status=result.status,
            tolerance=result.tolerance,
            ticket=ticket_response(result.ticket),
            matched_ticket=(
                ticket_response(result.matched_ticket)
                if result.matched_ticket is not None
                else None
            ),
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
