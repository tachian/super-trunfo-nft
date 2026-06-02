from random import Random

from super_trunfo_shared.cards import CardAttributes

CARD_NAME_PREFIXES = ("Solar", "Shadow", "Aqua", "Iron", "Storm", "Crystal")
CARD_NAME_ARCHETYPES = ("Titan", "Ranger", "Oracle", "Guardian", "Striker", "Sentinel")
COMMON_RARITY_RANGE = (1, 49)
RARE_RARITY_RANGE = (50, 74)
EPIC_RARITY_RANGE = (75, 89)
LEGENDARY_RARITY_RANGE = (90, 100)


class ProceduralCardAttributeGenerator:
    def __init__(self, random_source: Random | None = None) -> None:
        self.random_source = random_source or Random()

    def generate(self) -> CardAttributes:
        prefix = self.random_source.choice(CARD_NAME_PREFIXES)
        archetype = self.random_source.choice(CARD_NAME_ARCHETYPES)

        return CardAttributes(
            name=f"{prefix} {archetype}",
            speed=self.random_source.randint(30, 100),
            strength=self.random_source.randint(30, 100),
            intelligence=self.random_source.randint(30, 100),
            resistance=self.random_source.randint(30, 100),
            rarity=self.generate_rarity(),
        )

    def generate_rarity(self) -> int:
        roll = self.random_source.random()

        if roll < 0.50:
            return self.random_source.randint(*COMMON_RARITY_RANGE)

        if roll < 0.80:
            return self.random_source.randint(*RARE_RARITY_RANGE)

        if roll < 0.95:
            return self.random_source.randint(*EPIC_RARITY_RANGE)

        return self.random_source.randint(*LEGENDARY_RARITY_RANGE)
