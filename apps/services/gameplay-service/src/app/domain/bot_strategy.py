from dataclasses import dataclass
from typing import Protocol
from uuid import UUID, uuid5

from .entities import MATCH_DECK_SIZE, PlayableAttribute
from .exceptions import GameplayInvariantError

BOT_CARD_NAMESPACE = UUID("00000000-0000-4000-8000-000000000303")
DEFAULT_BEST_ATTRIBUTE_PROBABILITY = 0.7
DEFAULT_LEVEL_TOLERANCE = 20


class RandomSource(Protocol):
    def random(self) -> float:
        """Return a float in the [0.0, 1.0) interval."""

    def choice(self, values: tuple[PlayableAttribute, ...]) -> PlayableAttribute:
        """Choose one playable attribute."""


@dataclass(frozen=True)
class BattleCardProfile:
    card_id: UUID
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int

    @property
    def level(self) -> int:
        return self.speed + self.strength + self.intelligence + self.resistance + self.rarity

    def value_for(self, attribute: PlayableAttribute) -> int:
        return {
            PlayableAttribute.SPEED: self.speed,
            PlayableAttribute.STRENGTH: self.strength,
            PlayableAttribute.INTELLIGENCE: self.intelligence,
            PlayableAttribute.RESISTANCE: self.resistance,
            PlayableAttribute.RARITY: self.rarity,
        }[attribute]


@dataclass(frozen=True)
class BotDeck:
    owner_id: UUID
    cards: tuple[BattleCardProfile, ...]

    def __post_init__(self) -> None:
        if len(self.cards) != MATCH_DECK_SIZE:
            raise GameplayInvariantError("bot deck must contain exactly 10 cards")

    @property
    def average_level(self) -> float:
        return sum(card.level for card in self.cards) / MATCH_DECK_SIZE


@dataclass(frozen=True)
class BotStrategyConfig:
    best_attribute_probability: float = DEFAULT_BEST_ATTRIBUTE_PROBABILITY
    level_tolerance: int = DEFAULT_LEVEL_TOLERANCE

    def __post_init__(self) -> None:
        if self.best_attribute_probability < 0 or self.best_attribute_probability > 1:
            raise GameplayInvariantError("best attribute probability must be between 0 and 1")

        if self.level_tolerance < 0:
            raise GameplayInvariantError("bot deck level tolerance cannot be negative")


class BotStrategy:
    def __init__(
        self,
        random_source: RandomSource,
        config: BotStrategyConfig | None = None,
    ) -> None:
        self.random_source = random_source
        self.config = config or BotStrategyConfig()

    def choose_attribute(self, card: BattleCardProfile) -> PlayableAttribute:
        best_attribute = max(
            PlayableAttribute,
            key=lambda attribute: card.value_for(attribute),
        )

        if self.random_source.random() < self.config.best_attribute_probability:
            return best_attribute

        alternatives = tuple(
            attribute
            for attribute in PlayableAttribute
            if attribute != best_attribute
        )

        return self.random_source.choice(alternatives)

    def build_equivalent_deck(
        self,
        *,
        bot_id: UUID,
        player_cards: tuple[BattleCardProfile, ...],
    ) -> BotDeck:
        if len(player_cards) != MATCH_DECK_SIZE:
            raise GameplayInvariantError("player deck must contain exactly 10 cards")

        bot_cards = tuple(
            self._equivalent_bot_card(bot_id=bot_id, player_card=card)
            for card in player_cards
        )
        bot_deck = BotDeck(owner_id=bot_id, cards=bot_cards)
        level_gap = abs(bot_deck.average_level - average_level(player_cards))

        if level_gap > self.config.level_tolerance:
            raise GameplayInvariantError("bot deck is not equivalent to the player deck")

        return bot_deck

    def _equivalent_bot_card(
        self,
        *,
        bot_id: UUID,
        player_card: BattleCardProfile,
    ) -> BattleCardProfile:
        return BattleCardProfile(
            card_id=uuid5(BOT_CARD_NAMESPACE, f"{bot_id}:{player_card.card_id}"),
            speed=player_card.speed,
            strength=player_card.strength,
            intelligence=player_card.intelligence,
            resistance=player_card.resistance,
            rarity=player_card.rarity,
        )


def average_level(cards: tuple[BattleCardProfile, ...]) -> float:
    if not cards:
        raise GameplayInvariantError("cards cannot be empty")

    return sum(card.level for card in cards) / len(cards)
