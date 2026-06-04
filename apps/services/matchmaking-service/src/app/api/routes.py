from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.application.use_cases import GetQueueStatus
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


def create_matchmaking_router() -> APIRouter:
    router = APIRouter(tags=["matchmaking"])

    @router.post("/matchmaking/find", status_code=status.HTTP_202_ACCEPTED)
    async def find_match() -> dict[str, str]:
        return {
            "service": "matchmaking-service",
            "status": "planned",
            "task": "ST-402",
            "fallback": "pve-bot",
        }

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
