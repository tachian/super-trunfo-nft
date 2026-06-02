from datetime import UTC, datetime

from super_trunfo_shared.cards import (
    CardAttributes,
    calculate_card_level,
    calculate_expiration_date,
    calculate_expiration_days,
    card_uniqueness_hash,
)


def test_card_level_calculation() -> None:
    attributes = CardAttributes(
        name="Shadow Titan",
        speed=10,
        strength=20,
        intelligence=30,
        resistance=40,
        rarity=50,
    )

    assert calculate_card_level(attributes) == 150


def test_card_uniqueness_hash_changes_when_attributes_change() -> None:
    base = CardAttributes("Shadow Titan", 82, 91, 64, 76, 80)
    changed = CardAttributes("Shadow Titan", 82, 91, 65, 76, 80)

    assert card_uniqueness_hash(base) != card_uniqueness_hash(changed)


def test_card_uniqueness_hash_uses_canonical_sha256_payload() -> None:
    base = CardAttributes(" Shadow Titan ", 82, 91, 64, 76, 80)
    same_logical_card = CardAttributes("shadow titan", 82, 91, 64, 76, 80)

    assert len(card_uniqueness_hash(base)) == 64
    assert card_uniqueness_hash(base) == card_uniqueness_hash(same_logical_card)


def test_expiration_formula_uses_rarity_bonus() -> None:
    assert calculate_expiration_days(rarity=50) == 365
    assert calculate_expiration_days(rarity=80) == 401


def test_expiration_date_starts_from_creation_time() -> None:
    created_at = datetime(2026, 5, 18, tzinfo=UTC)

    assert calculate_expiration_date(rarity=50, created_at=created_at).year == 2027
