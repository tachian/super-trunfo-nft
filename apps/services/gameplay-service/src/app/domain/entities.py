from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
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

        object.__setattr__(self, "selected_attribute", PlayableAttribute(self.selected_attribute))


@dataclass(frozen=True)
class MatchScore:
    player: int
    opponent: int


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
