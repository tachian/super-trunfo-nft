from asyncio import Event, wait_for
from dataclasses import dataclass
from uuid import UUID

from app.application.use_cases import (
    GenerateProceduralCards,
    GenerateProceduralCardsCommand,
    GenerateProceduralCardsResult,
)


@dataclass(frozen=True)
class ProceduralCardGenerationWorkerConfig:
    owner_id: UUID
    family: str
    batch_size: int
    interval_seconds: float = 60.0


class ProceduralCardGenerationWorker:
    def __init__(
        self,
        generate_procedural_cards: GenerateProceduralCards,
        config: ProceduralCardGenerationWorkerConfig,
    ) -> None:
        self.generate_procedural_cards = generate_procedural_cards
        self.config = config

    def run_once(self) -> GenerateProceduralCardsResult:
        return self.generate_procedural_cards.execute(
            GenerateProceduralCardsCommand(
                owner_id=self.config.owner_id,
                family=self.config.family,
                quantity=self.config.batch_size,
            )
        )

    async def run_forever(self, stop_event: Event) -> None:
        while not stop_event.is_set():
            self.run_once()

            try:
                await wait_for(stop_event.wait(), timeout=self.config.interval_seconds)
            except TimeoutError:
                continue
