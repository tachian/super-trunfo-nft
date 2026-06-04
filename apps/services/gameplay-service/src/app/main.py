from super_trunfo_shared.api import create_service_app

from app.api.routes import create_gameplay_router
from app.infrastructure.repositories import InMemoryMatchRepository

SERVICE_NAME = "gameplay-service"
CONTEXT = "gameplay"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/match/{id}", "task": "ST-305"},
    {"method": "POST", "path": "/match/{id}/play", "task": "ST-305"},
    {"method": "GET", "path": "/match/{id}/replay", "task": "ST-304"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.match_repository = InMemoryMatchRepository()
app.include_router(create_gameplay_router())
