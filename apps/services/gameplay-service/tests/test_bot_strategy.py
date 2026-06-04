from uuid import UUID

import pytest
from app.domain.bot_strategy import (
    BattleCardProfile,
    BotStrategy,
    BotStrategyConfig,
)
from app.domain.entities import PlayableAttribute
from app.domain.exceptions import GameplayInvariantError


def test_bot_strategy_prefers_best_attribute_when_probability_matches() -> None:
    strategy = BotStrategy(
        FixedRandomSource(roll=0.1, chosen_attribute=PlayableAttribute.SPEED),
        BotStrategyConfig(best_attribute_probability=0.7),
    )

    assert strategy.choose_attribute(strong_card()) == PlayableAttribute.STRENGTH


def test_bot_strategy_can_choose_alternative_attribute_probabilistically() -> None:
    strategy = BotStrategy(
        FixedRandomSource(roll=0.9, chosen_attribute=PlayableAttribute.SPEED),
        BotStrategyConfig(best_attribute_probability=0.7),
    )

    assert strategy.choose_attribute(strong_card()) == PlayableAttribute.SPEED


def test_bot_strategy_builds_equivalent_deck() -> None:
    bot_id = UUID("99999999-9999-4999-8999-999999999303")
    player_cards = battle_cards()
    bot_deck = BotStrategy(FixedRandomSource()).build_equivalent_deck(
        bot_id=bot_id,
        player_cards=player_cards,
    )

    assert bot_deck.owner_id == bot_id
    assert len(bot_deck.cards) == 10
    assert bot_deck.average_level == 335.5
    assert bot_deck.average_level == sum(card.level for card in player_cards) / 10
    assert {card.card_id for card in bot_deck.cards}.isdisjoint(
        {card.card_id for card in player_cards}
    )


def test_bot_strategy_rejects_player_deck_without_10_cards() -> None:
    with pytest.raises(GameplayInvariantError, match="exactly 10"):
        BotStrategy(FixedRandomSource()).build_equivalent_deck(
            bot_id=UUID("99999999-9999-4999-8999-999999999303"),
            player_cards=battle_cards()[:9],
        )


def strong_card() -> BattleCardProfile:
    return BattleCardProfile(
        card_id=UUID("11111111-1111-4111-8111-000000000303"),
        speed=70,
        strength=95,
        intelligence=65,
        resistance=80,
        rarity=50,
    )


def battle_cards() -> tuple[BattleCardProfile, ...]:
    return tuple(
        BattleCardProfile(
            card_id=UUID(f"11111111-1111-4111-8111-{index:012d}"),
            speed=50 + index,
            strength=60,
            intelligence=70,
            resistance=80,
            rarity=70,
        )
        for index in range(1, 11)
    )


class FixedRandomSource:
    def __init__(
        self,
        roll: float = 0.1,
        chosen_attribute: PlayableAttribute = PlayableAttribute.SPEED,
    ) -> None:
        self.roll = roll
        self.chosen_attribute = chosen_attribute

    def random(self) -> float:
        return self.roll

    def choice(self, values: tuple[PlayableAttribute, ...]) -> PlayableAttribute:
        assert self.chosen_attribute in values

        return self.chosen_attribute
