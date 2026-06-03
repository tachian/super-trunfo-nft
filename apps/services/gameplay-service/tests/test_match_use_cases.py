from uuid import UUID

import pytest
from app.application.use_cases import (
    GetMatchState,
    GetMatchStateQuery,
    StartMatch,
    StartMatchCommand,
)
from app.domain.exceptions import MatchNotFoundError
from app.infrastructure.repositories import InMemoryMatchRepository


def test_start_match_persists_in_progress_match() -> None:
    repository = InMemoryMatchRepository()
    match = StartMatch(repository).execute(
        StartMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-111111111302"),
            opponent_id=UUID("22222222-2222-4222-8222-222222222302"),
            player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
            opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        )
    )

    assert repository.find_by_id(match.id) == match
    assert match.status == "in_progress"


def test_get_match_state_rejects_missing_match() -> None:
    with pytest.raises(MatchNotFoundError, match="not found"):
        GetMatchState(InMemoryMatchRepository()).execute(
            GetMatchStateQuery(
                match_id=UUID("33333333-3333-4333-8333-333333333302"),
            )
        )


def deck_ids(prefix: str, start: int) -> tuple[UUID, ...]:
    return tuple(UUID(f"{prefix}-{index:012d}") for index in range(start, start + 10))
