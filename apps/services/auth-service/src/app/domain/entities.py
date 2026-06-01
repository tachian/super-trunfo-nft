from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from super_trunfo_shared.cards import (
    CardAttributes,
    calculate_card_level,
    calculate_expiration_date,
)

INITIAL_ONBOARDING_CREDITS = 1


@dataclass(frozen=True)
class InitialCardTemplate:
    name: str
    family: str
    rarity_label: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int


INITIAL_DECK_TEMPLATES = (
    InitialCardTemplate("Aurora Runner", "sky", "common", 62, 56, 58, 55, 50),
    InitialCardTemplate("Granite Guard", "earth", "common", 52, 66, 54, 60, 52),
    InitialCardTemplate("Tide Scholar", "ocean", "common", 55, 52, 68, 56, 54),
    InitialCardTemplate("Ember Striker", "fire", "common", 60, 64, 54, 54, 56),
    InitialCardTemplate("Verdant Scout", "forest", "rare", 64, 54, 58, 56, 60),
    InitialCardTemplate("Iron Lynx", "metal", "rare", 58, 62, 55, 60, 62),
    InitialCardTemplate("Mist Oracle", "mystic", "rare", 55, 52, 68, 58, 64),
    InitialCardTemplate("Solar Warden", "light", "epic", 56, 64, 58, 60, 68),
    InitialCardTemplate("Night Corsair", "shadow", "epic", 64, 58, 62, 56, 70),
)


@dataclass(frozen=True)
class InitialDeckCard:
    id: UUID
    name: str
    family: str
    rarity_label: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int
    level: int
    expires_at: datetime


@dataclass(frozen=True)
class CreditLedgerEntry:
    id: UUID
    amount: int
    reason: str
    created_at: datetime


@dataclass(frozen=True)
class OnboardingRewards:
    initial_deck: tuple[InitialDeckCard, ...]
    initial_credits: int
    credit_ledger: tuple[CreditLedgerEntry, ...]
    granted_at: datetime


@dataclass(frozen=True)
class Player:
    nickname: str
    email: str
    password_hash: str
    id: UUID = field(default_factory=uuid4)
    rating: int = 1000
    credits: int = 0
    social_login_provider: str = "credentials"
    social_login_subject: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    onboarding: OnboardingRewards | None = None


def grant_initial_onboarding(player: Player) -> Player:
    if player.onboarding is not None:
        return player

    granted_at = player.created_at
    initial_deck = generate_initial_deck(owner_id=player.id, created_at=granted_at)
    credit_entry = CreditLedgerEntry(
        id=uuid5(NAMESPACE_URL, f"super-trunfo:initial-credit:{player.id}"),
        amount=INITIAL_ONBOARDING_CREDITS,
        reason="initial_deck_tenth_card_credit",
        created_at=granted_at,
    )
    rewards = OnboardingRewards(
        initial_deck=initial_deck,
        initial_credits=INITIAL_ONBOARDING_CREDITS,
        credit_ledger=(credit_entry,),
        granted_at=granted_at,
    )

    return replace(
        player,
        credits=player.credits + INITIAL_ONBOARDING_CREDITS,
        onboarding=rewards,
    )


def generate_initial_deck(*, owner_id: UUID, created_at: datetime) -> tuple[InitialDeckCard, ...]:
    cards: list[InitialDeckCard] = []

    for index, template in enumerate(INITIAL_DECK_TEMPLATES):
        attributes = CardAttributes(
            name=template.name,
            speed=template.speed,
            strength=template.strength,
            intelligence=template.intelligence,
            resistance=template.resistance,
            rarity=template.rarity,
        )
        cards.append(
            InitialDeckCard(
                id=uuid5(NAMESPACE_URL, f"super-trunfo:initial-card:{owner_id}:{index}"),
                name=template.name,
                family=template.family,
                rarity_label=template.rarity_label,
                speed=template.speed,
                strength=template.strength,
                intelligence=template.intelligence,
                resistance=template.resistance,
                rarity=template.rarity,
                level=calculate_card_level(attributes),
                expires_at=calculate_expiration_date(template.rarity, created_at),
            )
        )

    return tuple(cards)


@dataclass(frozen=True)
class AuthSession:
    player_id: UUID
    access_token: str
    token_type: str
    expires_in: int
