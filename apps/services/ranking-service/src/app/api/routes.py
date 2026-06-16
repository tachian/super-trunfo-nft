from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from super_trunfo_shared import DomainEvent

from app.application.use_cases import (
    GetFriendsRanking,
    GetFriendsRankingQuery,
    GetGlobalRanking,
    GetGlobalRankingQuery,
    RecalculatePlayerRating,
    RecalculatePlayerRatingCommand,
)
from app.domain.entities import LeaderboardEntry, Rating
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


class LeaderboardEntryResponse(RatingResponse):
    position: int


class RankingCacheResponse(BaseModel):
    hit: bool


class RankingLeaderboardResponse(BaseModel):
    service: str
    task: str
    scope: str
    total: int
    limit: int
    offset: int
    entries: list[LeaderboardEntryResponse]
    cache: RankingCacheResponse


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

    @router.get(
        "/ranking/global",
        operation_id="getGlobalRanking",
        response_model=RankingLeaderboardResponse,
    )
    async def global_ranking(
        request: Request,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> RankingLeaderboardResponse:
        result = GetGlobalRanking(
            request.app.state.rating_repository,
            request.app.state.leaderboard_cache,
        ).execute(GetGlobalRankingQuery(limit=limit, offset=offset))

        return leaderboard_response(
            scope="global",
            entries=result.entries,
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            cache_hit=result.cache_hit,
        )

    @router.get(
        "/ranking/friends",
        operation_id="getFriendsRanking",
        response_model=RankingLeaderboardResponse,
    )
    async def friends_ranking(
        request: Request,
        player_id: Annotated[UUID, Query()],
        friend_ids: Annotated[list[UUID] | None, Query()] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> RankingLeaderboardResponse:
        result = GetFriendsRanking(
            request.app.state.rating_repository,
            request.app.state.leaderboard_cache,
        ).execute(
            GetFriendsRankingQuery(
                player_id=player_id,
                friend_ids=tuple(friend_ids or ()),
                limit=limit,
                offset=offset,
            )
        )

        return leaderboard_response(
            scope="friends",
            entries=result.entries,
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            cache_hit=result.cache_hit,
        )

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
        if payload.winner_id == payload.loser_id:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "winner and loser must be different players"},
            )

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
        except RankingInvariantError as _exc:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid ranking recalculation"},
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


def leaderboard_response(
    *,
    scope: str,
    entries: tuple[LeaderboardEntry, ...],
    total: int,
    limit: int,
    offset: int,
    cache_hit: bool,
) -> RankingLeaderboardResponse:
    return RankingLeaderboardResponse(
        service="ranking-service",
        task="ST-504",
        scope=scope,
        total=total,
        limit=limit,
        offset=offset,
        entries=[leaderboard_entry_response(entry) for entry in entries],
        cache=RankingCacheResponse(hit=cache_hit),
    )


def leaderboard_entry_response(entry: LeaderboardEntry) -> LeaderboardEntryResponse:
    rating_payload = rating_response(entry.rating).model_dump()

    return LeaderboardEntryResponse(position=entry.position, **rating_payload)


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
