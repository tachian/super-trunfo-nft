from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.domain.entities import (
    Match,
    MatchParticipant,
    MatchStatus,
    ParticipantKind,
    PlayableAttribute,
    Round,
    create_match,
)
from app.domain.exceptions import GameplayInvariantError

PLAYER_ID = UUID("11111111-1111-4111-8111-111111111302")
OPPONENT_ID = UUID("22222222-2222-4222-8222-222222222302")


def test_create_match_stores_participants_status_and_initial_score() -> None:
    match = create_match(
        player_id=PLAYER_ID,
        opponent_id=OPPONENT_ID,
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        match_id=UUID("33333333-3333-4333-8333-333333333302"),
        created_at=datetime(2026, 6, 29, tzinfo=UTC),
    )

    assert match.id == UUID("33333333-3333-4333-8333-333333333302")
    assert match.player.id == PLAYER_ID
    assert match.player.kind == ParticipantKind.PLAYER
    assert match.opponent.id == OPPONENT_ID
    assert match.opponent.kind == ParticipantKind.PLAYER
    assert match.status == MatchStatus.IN_PROGRESS
    assert match.rounds == ()
    assert match.score.player == 0
    assert match.score.opponent == 0
    assert match.winner_id is None


def test_match_score_is_derived_from_round_winners() -> None:
    match = Match(
        id=UUID("33333333-3333-4333-8333-333333333302"),
        player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
        opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
        rounds=(
            round_result(1, PLAYER_ID),
            round_result(2, OPPONENT_ID),
            round_result(3, PLAYER_ID),
        ),
        status=MatchStatus.IN_PROGRESS,
        created_at=datetime(2026, 6, 29, tzinfo=UTC),
    )

    assert match.score.player == 2
    assert match.score.opponent == 1


def test_finished_match_requires_winner_and_finish_timestamp() -> None:
    with pytest.raises(GameplayInvariantError, match="winner"):
        Match(
            id=UUID("33333333-3333-4333-8333-333333333302"),
            player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
            opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
            rounds=(),
            status=MatchStatus.FINISHED,
            created_at=datetime(2026, 6, 29, tzinfo=UTC),
            finished_at=datetime(2026, 6, 29, 1, tzinfo=UTC),
        )


def test_finished_match_requires_finish_timestamp() -> None:
    with pytest.raises(GameplayInvariantError, match="finish timestamp"):
        Match(
            id=UUID("33333333-3333-4333-8333-333333333302"),
            player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
            opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
            rounds=(round_result(1, PLAYER_ID),),
            status=MatchStatus.FINISHED,
            created_at=datetime(2026, 6, 29, tzinfo=UTC),
            winner_id=PLAYER_ID,
        )


def test_unfinished_match_rejects_finish_timestamp() -> None:
    with pytest.raises(GameplayInvariantError, match="unfinished"):
        Match(
            id=UUID("33333333-3333-4333-8333-333333333302"),
            player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
            opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
            rounds=(),
            status=MatchStatus.IN_PROGRESS,
            created_at=datetime(2026, 6, 29, tzinfo=UTC),
            finished_at=datetime(2026, 6, 29, 1, tzinfo=UTC),
        )


def test_match_rejects_same_participant() -> None:
    with pytest.raises(GameplayInvariantError, match="participants"):
        Match(
            id=UUID("33333333-3333-4333-8333-333333333302"),
            player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
            opponent=participant(PLAYER_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
            rounds=(),
            status=MatchStatus.IN_PROGRESS,
            created_at=datetime(2026, 6, 29, tzinfo=UTC),
        )


def test_match_rejects_duplicated_round_numbers() -> None:
    with pytest.raises(GameplayInvariantError, match="duplicated round"):
        Match(
            id=UUID("33333333-3333-4333-8333-333333333302"),
            player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
            opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
            rounds=(round_result(1, PLAYER_ID), round_result(1, OPPONENT_ID)),
            status=MatchStatus.IN_PROGRESS,
            created_at=datetime(2026, 6, 29, tzinfo=UTC),
        )


def test_match_rejects_winner_outside_participants() -> None:
    with pytest.raises(GameplayInvariantError, match="winner"):
        Match(
            id=UUID("33333333-3333-4333-8333-333333333302"),
            player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
            opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
            rounds=(round_result(1, PLAYER_ID),),
            status=MatchStatus.FINISHED,
            created_at=datetime(2026, 6, 29, tzinfo=UTC),
            winner_id=UUID("99999999-9999-4999-8999-999999999999"),
            finished_at=datetime(2026, 6, 29, 1, tzinfo=UTC),
        )


def test_round_requires_positive_number() -> None:
    with pytest.raises(GameplayInvariantError, match="round number"):
        Round(
            number=0,
            player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
            selected_attribute=PlayableAttribute.SPEED,
            winner_id=PLAYER_ID,
            played_at=datetime(2026, 6, 29, tzinfo=UTC),
        )


def test_round_rejects_invalid_attribute() -> None:
    with pytest.raises(GameplayInvariantError, match="attribute"):
        Round(
            number=1,
            player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
            selected_attribute="luck",
            winner_id=PLAYER_ID,
            played_at=datetime(2026, 6, 29, tzinfo=UTC),
        )


def test_match_records_valid_round_without_accepting_score_mutation() -> None:
    match = create_match(
        player_id=PLAYER_ID,
        opponent_id=OPPONENT_ID,
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        created_at=datetime(2026, 6, 29, tzinfo=UTC),
    )

    updated_match = match.record_round(
        player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
        opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
        selected_attribute=PlayableAttribute.SPEED,
        winner_id=PLAYER_ID,
        played_at=datetime(2026, 6, 29, 1, tzinfo=UTC),
    )

    assert len(updated_match.rounds) == 1
    assert updated_match.rounds[0].number == 1
    assert updated_match.score.player == 1
    assert updated_match.score.opponent == 0


def test_match_rejects_card_outside_deck() -> None:
    match = create_match(
        player_id=PLAYER_ID,
        opponent_id=OPPONENT_ID,
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
    )

    with pytest.raises(GameplayInvariantError, match="player card"):
        match.record_round(
            player_card_id=UUID("cccccccc-cccc-4ccc-8ccc-000000000001"),
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
            selected_attribute=PlayableAttribute.SPEED,
        )


def test_match_rejects_card_replay() -> None:
    match = create_match(
        player_id=PLAYER_ID,
        opponent_id=OPPONENT_ID,
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
    )
    updated_match = match.record_round(
        player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
        opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
        selected_attribute=PlayableAttribute.SPEED,
    )

    with pytest.raises(GameplayInvariantError, match="already played"):
        updated_match.record_round(
            player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[1],
            selected_attribute=PlayableAttribute.STRENGTH,
        )


def test_match_rejects_opponent_card_replay() -> None:
    match = create_match(
        player_id=PLAYER_ID,
        opponent_id=OPPONENT_ID,
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
    )
    updated_match = match.record_round(
        player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
        opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
        selected_attribute=PlayableAttribute.SPEED,
    )

    with pytest.raises(GameplayInvariantError, match="already played"):
        updated_match.record_round(
            player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[1],
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
            selected_attribute=PlayableAttribute.STRENGTH,
        )


def test_match_rejects_round_winner_outside_participants() -> None:
    match = create_match(
        player_id=PLAYER_ID,
        opponent_id=OPPONENT_ID,
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
    )

    with pytest.raises(GameplayInvariantError, match="round winner"):
        match.record_round(
            player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[0],
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[0],
            selected_attribute=PlayableAttribute.SPEED,
            winner_id=UUID("99999999-9999-4999-8999-999999999999"),
        )


def test_match_rejects_round_when_not_in_progress() -> None:
    match = Match(
        id=UUID("33333333-3333-4333-8333-333333333302"),
        player=participant(PLAYER_ID, "aaaaaaaa-aaaa-4aaa-8aaa"),
        opponent=participant(OPPONENT_ID, "bbbbbbbb-bbbb-4bbb-8bbb"),
        rounds=(round_result(1, PLAYER_ID),),
        status=MatchStatus.FINISHED,
        created_at=datetime(2026, 6, 29, tzinfo=UTC),
        winner_id=PLAYER_ID,
        finished_at=datetime(2026, 6, 29, 1, tzinfo=UTC),
    )

    with pytest.raises(GameplayInvariantError, match="not in progress"):
        match.record_round(
            player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[1],
            opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[1],
            selected_attribute=PlayableAttribute.SPEED,
        )


def test_participant_requires_10_unique_cards() -> None:
    with pytest.raises(GameplayInvariantError, match="exactly 10"):
        MatchParticipant(
            id=PLAYER_ID,
            kind=ParticipantKind.PLAYER,
            deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[:9],
        )


def participant(player_id: UUID, prefix: str) -> MatchParticipant:
    return MatchParticipant(
        id=player_id,
        kind=ParticipantKind.PLAYER,
        deck_card_ids=deck_ids(prefix, 1),
    )


def round_result(number: int, winner_id: UUID) -> Round:
    return Round(
        number=number,
        player_card_id=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1)[number - 1],
        opponent_card_id=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1)[number - 1],
        selected_attribute=PlayableAttribute.SPEED,
        winner_id=winner_id,
        played_at=datetime(2026, 6, 29, number, tzinfo=UTC),
    )


def deck_ids(prefix: str, start: int) -> tuple[UUID, ...]:
    return tuple(UUID(f"{prefix}-{index:012d}") for index in range(start, start + 10))
