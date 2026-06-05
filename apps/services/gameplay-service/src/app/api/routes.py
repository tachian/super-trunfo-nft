import asyncio
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from app.application.use_cases import (
    GetMatchState,
    GetMatchStateQuery,
    PlayRound,
    PlayRoundCommand,
)
from app.domain.entities import (
    GameplayRealtimeEvent,
    Match,
    MatchParticipant,
    PlayableAttribute,
    Round,
)
from app.domain.exceptions import MatchNotFoundError, MatchPlayValidationError


class ParticipantResponse(BaseModel):
    id: str
    kind: str
    deck_card_ids: list[str]


class RoundResponse(BaseModel):
    number: int
    player_card_id: str
    opponent_card_id: str
    selected_attribute: str
    winner_id: str | None
    played_at: datetime


class MatchScoreResponse(BaseModel):
    player: int
    opponent: int


class MatchResponse(BaseModel):
    id: str
    player: ParticipantResponse
    opponent: ParticipantResponse
    rounds: list[RoundResponse]
    score: MatchScoreResponse
    status: str
    winner_id: str | None
    created_at: datetime
    finished_at: datetime | None


class PlayRoundRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_card_id: UUID
    opponent_card_id: UUID
    selected_attribute: PlayableAttribute


class MatchReplayResponse(BaseModel):
    match_id: str
    rounds: list[RoundResponse]


class GameplayRealtimeEventResponse(BaseModel):
    id: str
    name: str
    schema_version: str
    match_id: str
    payload: dict[str, Any]
    occurred_at: datetime


def create_gameplay_router() -> APIRouter:
    router = APIRouter(tags=["gameplay"])

    @router.websocket("/match/{match_id}/events")
    async def match_events(match_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        event_bus = websocket.app.state.gameplay_realtime_event_bus
        cursor = 0

        try:
            while True:
                events = event_bus.events_for_match(match_id, after_index=cursor)

                for event in events:
                    await websocket.send_json(realtime_event_payload(event))

                cursor += len(events)

                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=0.05)
                except TimeoutError:
                    continue
        except WebSocketDisconnect:
            return

    @router.get(
        "/match/{match_id}",
        operation_id="getMatchState",
        response_model=MatchResponse,
        responses={404: {"description": "Match not found"}},
    )
    async def get_match(
        match_id: UUID,
        request: Request,
    ) -> MatchResponse | JSONResponse:
        use_case = GetMatchState(request.app.state.match_repository)

        try:
            match = use_case.execute(GetMatchStateQuery(match_id=match_id))
        except MatchNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Match not found."},
            )

        return match_response(match)

    @router.post(
        "/match/{match_id}/play",
        operation_id="playRound",
        response_model=MatchResponse,
        responses={
            400: {"description": "Invalid round play"},
            404: {"description": "Match not found"},
        },
    )
    async def play_round(
        match_id: UUID,
        payload: PlayRoundRequest,
        request: Request,
    ) -> MatchResponse | JSONResponse:
        use_case = PlayRound(
            request.app.state.match_repository,
            request.app.state.gameplay_realtime_event_bus,
        )

        try:
            match = use_case.execute(
                PlayRoundCommand(
                    match_id=match_id,
                    player_card_id=payload.player_card_id,
                    opponent_card_id=payload.opponent_card_id,
                    selected_attribute=payload.selected_attribute,
                )
            )
        except MatchNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Match not found."},
            )
        except MatchPlayValidationError as exc:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(exc)},
            )

        return match_response(match)

    @router.get(
        "/match/{match_id}/replay",
        operation_id="getMatchReplay",
        response_model=MatchReplayResponse,
        responses={404: {"description": "Match not found"}},
    )
    async def match_replay(
        match_id: UUID,
        request: Request,
    ) -> MatchReplayResponse | JSONResponse:
        use_case = GetMatchState(request.app.state.match_repository)

        try:
            match = use_case.execute(GetMatchStateQuery(match_id=match_id))
        except MatchNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Match not found."},
            )

        return MatchReplayResponse(
            match_id=str(match.id),
            rounds=[round_response(round_item) for round_item in match.rounds],
        )

    return router


def match_response(match: Match) -> MatchResponse:
    return MatchResponse(
        id=str(match.id),
        player=participant_response(match.player),
        opponent=participant_response(match.opponent),
        rounds=[round_response(round_item) for round_item in match.rounds],
        score=MatchScoreResponse(
            player=match.score.player,
            opponent=match.score.opponent,
        ),
        status=match.status.value,
        winner_id=str(match.winner_id) if match.winner_id else None,
        created_at=match.created_at,
        finished_at=match.finished_at,
    )


def participant_response(participant: MatchParticipant) -> ParticipantResponse:
    return ParticipantResponse(
        id=str(participant.id),
        kind=participant.kind.value,
        deck_card_ids=[str(card_id) for card_id in participant.deck_card_ids],
    )


def round_response(round_item: Round) -> RoundResponse:
    return RoundResponse(
        number=round_item.number,
        player_card_id=str(round_item.player_card_id),
        opponent_card_id=str(round_item.opponent_card_id),
        selected_attribute=round_item.selected_attribute.value,
        winner_id=str(round_item.winner_id) if round_item.winner_id else None,
        played_at=round_item.played_at,
    )


def realtime_event_payload(event: GameplayRealtimeEvent) -> dict[str, Any]:
    return GameplayRealtimeEventResponse(
        id=str(event.id),
        name=event.name.value,
        schema_version=event.schema_version,
        match_id=str(event.match_id),
        payload=event.payload,
        occurred_at=event.occurred_at,
    ).model_dump(mode="json")
