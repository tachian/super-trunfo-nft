from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from app.domain.entities import Card, create_card
from app.domain.exceptions import CardInvariantError
from super_trunfo_shared.cards import (
    CardAttributes,
    calculate_expiration_days,
    card_uniqueness_hash,
)


def test_create_card_models_owner_attributes_family_level_and_validity() -> None:
    owner_id = UUID("11111111-1111-4111-8111-111111111111")
    card_id = UUID("22222222-2222-4222-8222-222222222222")
    created_at = datetime(2026, 6, 15, tzinfo=UTC)
    attributes = CardAttributes(
        name="Solar Lynx",
        speed=70,
        strength=62,
        intelligence=58,
        resistance=64,
        rarity=80,
    )

    card = create_card(
        owner_id=owner_id,
        attributes=attributes,
        family=" solar ",
        card_id=card_id,
        created_at=created_at,
    )

    assert card.id == card_id
    assert card.owner_id == owner_id
    assert card.attributes == attributes
    assert card.family == "solar"
    assert card.level == 334
    assert card.uniqueness_hash == card_uniqueness_hash(attributes)
    assert card.expires_at == created_at + timedelta(days=calculate_expiration_days(80))
    assert card.is_valid_at(created_at + timedelta(days=1))
    assert card.is_expired_at(card.expires_at)


def test_card_rejects_blank_family() -> None:
    with pytest.raises(CardInvariantError, match="family"):
        create_card(
            owner_id=UUID("11111111-1111-4111-8111-111111111111"),
            attributes=valid_attributes(),
            family=" ",
        )


def test_card_rejects_attributes_outside_supported_range() -> None:
    with pytest.raises(CardInvariantError, match="between 0 and 100"):
        create_card(
            owner_id=UUID("11111111-1111-4111-8111-111111111111"),
            attributes=CardAttributes(
                name="Broken Card",
                speed=101,
                strength=62,
                intelligence=58,
                resistance=64,
                rarity=80,
            ),
            family="solar",
        )


def test_card_rejects_expiration_before_creation() -> None:
    created_at = datetime(2026, 6, 15, tzinfo=UTC)

    with pytest.raises(CardInvariantError, match="expiration"):
        Card(
            id=UUID("22222222-2222-4222-8222-222222222222"),
            owner_id=UUID("11111111-1111-4111-8111-111111111111"),
            attributes=valid_attributes(),
            family="solar",
            created_at=created_at,
            expires_at=created_at,
        )


def valid_attributes() -> CardAttributes:
    return CardAttributes(
        name="Solar Lynx",
        speed=70,
        strength=62,
        intelligence=58,
        resistance=64,
        rarity=80,
    )
