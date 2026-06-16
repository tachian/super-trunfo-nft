from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_ranking_router
from app.infrastructure.repositories import InMemoryRatingRepository

SERVICE_NAME = "ranking-service"
CONTEXT = "ranking"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/ranking/global", "task": "ST-504"},
    {"method": "GET", "path": "/ranking/friends", "task": "ST-504"},
    {"method": "POST", "path": "/ranking/recalculate", "task": "ST-503"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.rating_repository = InMemoryRatingRepository()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.include_router(create_ranking_router())
