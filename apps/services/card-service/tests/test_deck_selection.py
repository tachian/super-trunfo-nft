from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.application.use_cases import SelectDeck, SelectDeckCommand
from app.domain.entities import Card, create_card, create_deck
from app.domain.exceptions import CardInvariantError, DeckCardNotFoundError, DeckSelectionError
from app.infrastructure.repositories import InMemoryCardRepository, InMemoryDeckRepository
from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.cards import CardAttributes

OWNER_ID = UUID("11111111-1111-4111-8111-111111111301")


def test_deck_requires_exactly_10_cards() -> None:
    with pytest.raises(CardInvariantError, match="exactly 10"):
        create_deck(owner_id=OWNER_ID, cards=valid_cards(9))


def test_deck_rejects_duplicated_cards() -> None:
    card = valid_cards(1)[0]

    with pytest.raises(CardInvariantError, match="duplicated"):
        create_deck(owner_id=OWNER_ID, cards=(card,) * 10)


def test_deck_rejects_expired_cards() -> None:
    cards = list(valid_cards(9))
    cards.append(expired_card(10))

    with pytest.raises(CardInvariantError, match="expired"):
        create_deck(owner_id=OWNER_ID, cards=tuple(cards))


def test_select_deck_persists_average_level_and_publishes_event() -> None:
    card_repository = InMemoryCardRepository()
    deck_repository = InMemoryDeckRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="card-service", context="cards")
    cards = valid_cards(10)

    for card in cards:
        card_repository.add(card)

    result = SelectDeck(card_repository, deck_repository, event_publisher).execute(
        SelectDeckCommand(
            owner_id=OWNER_ID,
            card_ids=tuple(card.id for card in cards),
        )
    )

    events = event_publisher.published_events()

    assert deck_repository.find_active_by_owner(OWNER_ID) == result.deck
    assert result.deck.card_ids == tuple(card.id for card in cards)
    assert result.deck.average_level == 315.5
    assert len(events) == 1
    assert events[0].name == "DeckSelected"
    assert events[0].payload["schema_version"] == "1.0.0"
    assert events[0].payload["owner_id"] == str(OWNER_ID)
    assert events[0].payload["card_ids"] == [str(card.id) for card in cards]
    assert events[0].payload["average_level"] == 315.5


def test_select_deck_rejects_card_from_another_owner() -> None:
    card_repository = InMemoryCardRepository()
    cards = list(valid_cards(9))
    cards.append(valid_card(10, owner_id=UUID("99999999-9999-4999-8999-999999999301")))

    for card in cards:
        card_repository.add(card)

    with pytest.raises(DeckSelectionError, match="owner"):
        SelectDeck(
            card_repository,
            InMemoryDeckRepository(),
            InMemoryDomainEventPublisher(service_name="card-service", context="cards"),
        ).execute(
            SelectDeckCommand(
                owner_id=OWNER_ID,
                card_ids=tuple(card.id for card in cards),
            )
        )


def test_select_deck_rejects_missing_card() -> None:
    with pytest.raises(DeckCardNotFoundError, match="not found"):
        SelectDeck(
            InMemoryCardRepository(),
            InMemoryDeckRepository(),
            InMemoryDomainEventPublisher(service_name="card-service", context="cards"),
        ).execute(
            SelectDeckCommand(
                owner_id=OWNER_ID,
                card_ids=tuple(card.id for card in valid_cards(10)),
            )
        )


def valid_cards(quantity: int) -> tuple[Card, ...]:
    return tuple(valid_card(index) for index in range(1, quantity + 1))


def valid_card(index: int, *, owner_id: UUID = OWNER_ID) -> Card:
    return create_card(
        owner_id=owner_id,
        attributes=CardAttributes(
            name=f"Deck Card {index}",
            speed=50 + index,
            strength=60,
            intelligence=70,
            resistance=80,
            rarity=50,
        ),
        family="solar",
        card_id=UUID(f"22222222-2222-4222-8222-{index:012d}"),
        created_at=datetime(2026, 6, 1, tzinfo=UTC),
    )


def expired_card(index: int) -> Card:
    return create_card(
        owner_id=OWNER_ID,
        attributes=CardAttributes(
            name=f"Expired Card {index}",
            speed=50,
            strength=60,
            intelligence=70,
            resistance=80,
            rarity=50,
        ),
        family="solar",
        card_id=UUID(f"33333333-3333-4333-8333-{index:012d}"),
        created_at=datetime(2020, 1, 1, tzinfo=UTC),
    )
