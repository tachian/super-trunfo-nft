from uuid import UUID

import pytest
from app.application.use_cases import (
    GetMatchState,
    GetMatchStateQuery,
    PlayRound,
    PlayRoundCommand,
    StartMatch,
    StartMatchCommand,
)
from app.domain.entities import PlayableAttribute
from app.domain.exceptions import MatchNotFoundError, MatchPlayValidationError
from app.infrastructure.repositories import (
    InMemoryGameplayRealtimeEventBus,
    InMemoryMatchRepository,
)


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


def test_play_round_persists_authoritative_round() -> None:
    repository = InMemoryMatchRepository()
    match = StartMatch(repository).execute(
        StartMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-111111111302"),
            opponent_id=UUID("22222222-2222-4222-8222-222222222302"),
            player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
            opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        )
    )

    updated_match = PlayRound(repository).execute(
        PlayRoundCommand(
            match_id=match.id,
            player_card_id=match.player.deck_card_ids[0],
            opponent_card_id=match.opponent.deck_card_ids[0],
            selected_attribute=PlayableAttribute.SPEED,
        )
    )

    assert repository.find_by_id(match.id) == updated_match
    assert len(updated_match.rounds) == 1
    assert updated_match.rounds[0].selected_attribute == PlayableAttribute.SPEED


def test_play_round_publishes_realtime_events() -> None:
    repository = InMemoryMatchRepository()
    event_bus = InMemoryGameplayRealtimeEventBus()
    match = StartMatch(repository).execute(
        StartMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-111111111302"),
            opponent_id=UUID("22222222-2222-4222-8222-222222222302"),
            player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
            opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        )
    )

    PlayRound(repository, event_bus).execute(
        PlayRoundCommand(
            match_id=match.id,
            player_card_id=match.player.deck_card_ids[0],
            opponent_card_id=match.opponent.deck_card_ids[0],
            selected_attribute=PlayableAttribute.SPEED,
        )
    )

    events = event_bus.events_for_match(match.id)

    assert [event.name.value for event in events] == [
        "AttributeSelected",
        "RoundFinished",
        "MatchResultUpdated",
        "PlayerRankUpdated",
    ]
    assert events[0].payload["selected_attribute"] == "speed"
    assert events[2].payload["score"] == {"player": 0, "opponent": 0}


def test_play_round_rejects_replayed_card() -> None:
    repository = InMemoryMatchRepository()
    match = StartMatch(repository).execute(
        StartMatchCommand(
            player_id=UUID("11111111-1111-4111-8111-111111111302"),
            opponent_id=UUID("22222222-2222-4222-8222-222222222302"),
            player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
            opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        )
    )
    play_round = PlayRound(repository)
    play_round.execute(
        PlayRoundCommand(
            match_id=match.id,
            player_card_id=match.player.deck_card_ids[0],
            opponent_card_id=match.opponent.deck_card_ids[0],
            selected_attribute=PlayableAttribute.SPEED,
        )
    )

    with pytest.raises(MatchPlayValidationError, match="already played"):
        play_round.execute(
            PlayRoundCommand(
                match_id=match.id,
                player_card_id=match.player.deck_card_ids[0],
                opponent_card_id=match.opponent.deck_card_ids[1],
                selected_attribute=PlayableAttribute.STRENGTH,
            )
        )


def deck_ids(prefix: str, start: int) -> tuple[UUID, ...]:
    return tuple(UUID(f"{prefix}-{index:012d}") for index in range(start, start + 10))
