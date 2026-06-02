from random import Random

from super_trunfo_shared.cards import CardAttributes


CARD_NAME_PREFIXES = ("Solar", "Shadow", "Aqua", "Iron", "Storm", "Crystal")
CARD_NAME_ARCHETYPES = ("Titan", "Ranger", "Oracle", "Guardian", "Striker", "Sentinel")


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
            rarity=self.random_source.randint(1, 100),
        )
