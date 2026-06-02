from uuid import UUID

from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_cards_router
from app.application.use_cases import GenerateProceduralCards
from app.infrastructure.generators import ProceduralCardAttributeGenerator
from app.infrastructure.repositories import InMemoryCardRepository, InMemoryCardSearchIndex
from app.infrastructure.workers import (
    ProceduralCardGenerationWorker,
    ProceduralCardGenerationWorkerConfig,
)

SERVICE_NAME = "card-service"
CONTEXT = "cards"
SYSTEM_CARD_OWNER_ID = UUID("00000000-0000-4000-8000-000000000204")
PLANNED_ROUTES = [
    {"method": "GET", "path": "/cards", "task": "ST-201"},
    {"method": "GET", "path": "/cards/{id}", "task": "ST-201"},
    {"method": "POST", "path": "/cards/sample/generate", "task": "ST-202"},
    {"method": "POST", "path": "/cards/select-deck", "task": "ST-301"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.card_repository = InMemoryCardRepository()
app.state.card_attribute_generator = ProceduralCardAttributeGenerator()
app.state.card_search_index = InMemoryCardSearchIndex()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.state.procedural_card_worker = ProceduralCardGenerationWorker(
    GenerateProceduralCards(
        app.state.card_repository,
        app.state.card_attribute_generator,
        app.state.card_search_index,
        app.state.domain_event_publisher,
    ),
    ProceduralCardGenerationWorkerConfig(
        owner_id=SYSTEM_CARD_OWNER_ID,
        family="shop",
        batch_size=10,
    ),
)
app.include_router(create_cards_router())
