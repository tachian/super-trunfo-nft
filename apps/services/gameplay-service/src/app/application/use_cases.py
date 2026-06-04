from dataclasses import dataclass
from uuid import UUID

from app.domain.entities import Match, ParticipantKind, create_match
from app.domain.exceptions import MatchNotFoundError
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
