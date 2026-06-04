from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Match, ParticipantKind, PlayableAttribute, create_match
from app.domain.exceptions import (
    GameplayInvariantError,
    MatchNotFoundError,
    MatchPlayValidationError,
)
from app.domain.repositories import MatchRepository


@dataclass(frozen=True)
class StartMatchCommand:
    player_id: UUID
    opponent_id: UUID
    player_deck_card_ids: tuple[UUID, ...]
    opponent_deck_card_ids: tuple[UUID, ...]
    opponent_kind: ParticipantKind = ParticipantKind.PLAYER


@dataclass(frozen=True)
class GetMatchStateQuery:
    match_id: UUID


@dataclass(frozen=True)
class PlayRoundCommand:
    match_id: UUID
    player_card_id: UUID
    opponent_card_id: UUID
    selected_attribute: PlayableAttribute


class StartMatch:
    def __init__(self, repository: MatchRepository) -> None:
        self.repository = repository

    def execute(self, command: StartMatchCommand) -> Match:
        match = create_match(
            player_id=command.player_id,
            opponent_id=command.opponent_id,
            player_deck_card_ids=command.player_deck_card_ids,
            opponent_deck_card_ids=command.opponent_deck_card_ids,
            opponent_kind=command.opponent_kind,
        )

        self.repository.save(match)

        return match


class GetMatchState:
    def __init__(self, repository: MatchRepository) -> None:
        self.repository = repository

    def execute(self, query: GetMatchStateQuery) -> Match:
        match = self.repository.find_by_id(query.match_id)

        if match is None:
            raise MatchNotFoundError("match was not found")

        return match


class PlayRound:
    def __init__(self, repository: MatchRepository) -> None:
        self.repository = repository

    def execute(self, command: PlayRoundCommand) -> Match:
        match = self.repository.find_by_id(command.match_id)

        if match is None:
            raise MatchNotFoundError("match was not found")

        try:
            updated_match = match.record_round(
                player_card_id=command.player_card_id,
                opponent_card_id=command.opponent_card_id,
                selected_attribute=command.selected_attribute,
            )
        except GameplayInvariantError as exc:
            raise MatchPlayValidationError(str(exc)) from exc

        self.repository.save(updated_match)

        return updated_match
