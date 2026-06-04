from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.application.use_cases import GetMatchState, GetMatchStateQuery
from app.domain.entities import Match, MatchParticipant, Round
from app.domain.exceptions import MatchNotFoundError


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


def create_gameplay_router() -> APIRouter:
    router = APIRouter(tags=["gameplay"])

    @router.get(
        "/match/{match_id}",
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

    @router.post("/match/{match_id}/play", status_code=status.HTTP_202_ACCEPTED)
    async def play_round(match_id: str) -> dict[str, str]:
        return {
            "service": "gameplay-service",
            "match_id": match_id,
            "status": "planned",
            "task": "ST-305",
        }

    @router.get("/match/{match_id}/replay", status_code=status.HTTP_202_ACCEPTED)
    async def match_replay(match_id: str) -> dict[str, str]:
        return {
            "service": "gameplay-service",
            "match_id": match_id,
            "status": "planned",
            "task": "ST-304",
        }

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
