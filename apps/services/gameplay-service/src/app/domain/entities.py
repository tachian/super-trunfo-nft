from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from .exceptions import GameplayInvariantError

MATCH_DECK_SIZE = 10


class MatchStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABANDONED = "abandoned"


class ParticipantKind(StrEnum):
    PLAYER = "player"
    BOT = "bot"


class PlayableAttribute(StrEnum):
    SPEED = "speed"
    STRENGTH = "strength"
    INTELLIGENCE = "intelligence"
    RESISTANCE = "resistance"
    RARITY = "rarity"


class GameplayRealtimeEventName(StrEnum):
    ATTRIBUTE_SELECTED = "AttributeSelected"
    ROUND_FINISHED = "RoundFinished"
    MATCH_RESULT_UPDATED = "MatchResultUpdated"
    PLAYER_RANK_UPDATED = "PlayerRankUpdated"


@dataclass(frozen=True)
class MatchParticipant:
    id: UUID
    kind: ParticipantKind
    deck_card_ids: tuple[UUID, ...]

    def __post_init__(self) -> None:
        normalized_kind = ParticipantKind(self.kind)

        if len(self.deck_card_ids) != MATCH_DECK_SIZE:
            raise GameplayInvariantError("match participant deck must contain exactly 10 cards")

        if len(set(self.deck_card_ids)) != MATCH_DECK_SIZE:
            raise GameplayInvariantError("match participant deck cannot contain duplicated cards")

        object.__setattr__(self, "kind", normalized_kind)


@dataclass(frozen=True)
class Round:
    number: int
    player_card_id: UUID
    opponent_card_id: UUID
    selected_attribute: PlayableAttribute
    winner_id: UUID | None
    played_at: datetime

    def __post_init__(self) -> None:
        if self.number < 1:
            raise GameplayInvariantError("round number must be greater than zero")

        try:
            selected_attribute = PlayableAttribute(self.selected_attribute)
        except ValueError as exc:
            raise GameplayInvariantError("selected attribute is invalid") from exc

        object.__setattr__(self, "selected_attribute", selected_attribute)


@dataclass(frozen=True)
class MatchScore:
    player: int
    opponent: int


@dataclass(frozen=True)
class GameplayRealtimeEvent:
    id: UUID
    name: GameplayRealtimeEventName
    match_id: UUID
    payload: dict[str, Any]
    occurred_at: datetime
    schema_version: str = "1.0.0"

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", GameplayRealtimeEventName(self.name))


@dataclass(frozen=True)
class Match:
    id: UUID
    player: MatchParticipant
    opponent: MatchParticipant
    rounds: tuple[Round, ...]
    status: MatchStatus
    created_at: datetime
    winner_id: UUID | None = None
    finished_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_status = MatchStatus(self.status)
        round_numbers = [round_item.number for round_item in self.rounds]

        if self.player.id == self.opponent.id:
            raise GameplayInvariantError("match participants must be different")

        if len(set(round_numbers)) != len(round_numbers):
            raise GameplayInvariantError("match cannot contain duplicated round numbers")

        if normalized_status == MatchStatus.FINISHED and self.winner_id is None:
            raise GameplayInvariantError("finished match must have a winner")

        if normalized_status == MatchStatus.FINISHED and self.finished_at is None:
            raise GameplayInvariantError("finished match must have a finish timestamp")

        if normalized_status != MatchStatus.FINISHED and self.finished_at is not None:
            raise GameplayInvariantError("unfinished match cannot have a finish timestamp")

        if self.winner_id is not None and self.winner_id not in (self.player.id, self.opponent.id):
            raise GameplayInvariantError("match winner must be one of the participants")

        object.__setattr__(self, "status", normalized_status)

    @property
    def score(self) -> MatchScore:
        player_score = 0
        opponent_score = 0

        for round_item in self.rounds:
            if round_item.winner_id == self.player.id:
                player_score += 1
            elif round_item.winner_id == self.opponent.id:
                opponent_score += 1

        return MatchScore(player=player_score, opponent=opponent_score)

    @property
    def used_player_card_ids(self) -> tuple[UUID, ...]:
        return tuple(round_item.player_card_id for round_item in self.rounds)

    @property
    def used_opponent_card_ids(self) -> tuple[UUID, ...]:
        return tuple(round_item.opponent_card_id for round_item in self.rounds)

    def record_round(
        self,
        *,
        player_card_id: UUID,
        opponent_card_id: UUID,
        selected_attribute: PlayableAttribute | str,
        winner_id: UUID | None = None,
        played_at: datetime | None = None,
    ) -> "Match":
        if self.status != MatchStatus.IN_PROGRESS:
            raise GameplayInvariantError("match is not in progress")

        if player_card_id not in self.player.deck_card_ids:
            raise GameplayInvariantError("player card is not part of the match deck")

        if opponent_card_id not in self.opponent.deck_card_ids:
            raise GameplayInvariantError("opponent card is not part of the match deck")

        if player_card_id in self.used_player_card_ids:
            raise GameplayInvariantError("player card was already played in this match")

        if opponent_card_id in self.used_opponent_card_ids:
            raise GameplayInvariantError("opponent card was already played in this match")

        if winner_id is not None and winner_id not in (self.player.id, self.opponent.id):
            raise GameplayInvariantError("round winner must be one of the participants")

        return Match(
            id=self.id,
            player=self.player,
            opponent=self.opponent,
            rounds=(
                *self.rounds,
                Round(
                    number=len(self.rounds) + 1,
                    player_card_id=player_card_id,
                    opponent_card_id=opponent_card_id,
                    selected_attribute=selected_attribute,
                    winner_id=winner_id,
                    played_at=played_at or datetime.now(UTC),
                ),
            ),
            status=self.status,
            created_at=self.created_at,
            winner_id=self.winner_id,
            finished_at=self.finished_at,
        )


def create_match(
    *,
    player_id: UUID,
    opponent_id: UUID,
    player_deck_card_ids: tuple[UUID, ...],
    opponent_deck_card_ids: tuple[UUID, ...],
    opponent_kind: ParticipantKind = ParticipantKind.PLAYER,
    match_id: UUID | None = None,
    created_at: datetime | None = None,
) -> Match:
    return Match(
        id=match_id or uuid4(),
        player=MatchParticipant(
            id=player_id,
            kind=ParticipantKind.PLAYER,
            deck_card_ids=player_deck_card_ids,
        ),
        opponent=MatchParticipant(
            id=opponent_id,
            kind=opponent_kind,
            deck_card_ids=opponent_deck_card_ids,
        ),
        rounds=(),
        status=MatchStatus.IN_PROGRESS,
        created_at=created_at or datetime.now(UTC),
    )


def round_realtime_events(
    *,
    match: Match,
    round_item: Round,
    occurred_at: datetime | None = None,
) -> tuple[GameplayRealtimeEvent, ...]:
    event_time = occurred_at or datetime.now(UTC)
    winner_id = str(round_item.winner_id) if round_item.winner_id else None

    return (
        GameplayRealtimeEvent(
            id=uuid4(),
            name=GameplayRealtimeEventName.ATTRIBUTE_SELECTED,
            match_id=match.id,
            payload={
                "round_number": round_item.number,
                "selected_attribute": round_item.selected_attribute.value,
                "player_card_id": str(round_item.player_card_id),
                "opponent_card_id": str(round_item.opponent_card_id),
            },
            occurred_at=event_time,
        ),
        GameplayRealtimeEvent(
            id=uuid4(),
            name=GameplayRealtimeEventName.ROUND_FINISHED,
            match_id=match.id,
            payload={
                "round_number": round_item.number,
                "winner_id": winner_id,
                "played_at": round_item.played_at.isoformat(),
            },
            occurred_at=event_time,
        ),
        GameplayRealtimeEvent(
            id=uuid4(),
            name=GameplayRealtimeEventName.MATCH_RESULT_UPDATED,
            match_id=match.id,
            payload={
                "status": match.status.value,
                "winner_id": str(match.winner_id) if match.winner_id else None,
                "score": {
                    "player": match.score.player,
                    "opponent": match.score.opponent,
                },
            },
            occurred_at=event_time,
        ),
        GameplayRealtimeEvent(
            id=uuid4(),
            name=GameplayRealtimeEventName.PLAYER_RANK_UPDATED,
            match_id=match.id,
            payload={
                "player_id": str(match.player.id),
                "opponent_id": str(match.opponent.id),
                "source": "gameplay-round-result",
                "score": {
                    "player": match.score.player,
                    "opponent": match.score.opponent,
                },
            },
            occurred_at=event_time,
        ),
    )
