from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_social_router
from app.infrastructure.repositories import InMemorySocialRepository

SERVICE_NAME = "social-service"
CONTEXT = "social"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/friends", "task": "ST-801"},
    {"method": "POST", "path": "/friends/invite", "task": "ST-801"},
    {"method": "POST", "path": "/friends/invite/{invite_id}/accept", "task": "ST-801"},
    {"method": "POST", "path": "/friends/invite/{invite_id}/reject", "task": "ST-801"},
    {"method": "GET", "path": "/guilds", "task": "ST-803"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.social_repository = InMemorySocialRepository()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.include_router(create_social_router())
