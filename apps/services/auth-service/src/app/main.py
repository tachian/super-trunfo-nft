from super_trunfo_shared.api import create_service_app

from app.api.routes import create_identity_router
from app.infrastructure.repositories import InMemoryPlayerRepository

SERVICE_NAME = "auth-service"
CONTEXT = "identity"
PLANNED_ROUTES = [
    {"method": "POST", "path": "/auth/register", "task": "ST-101"},
    {"method": "POST", "path": "/auth/login", "task": "ST-101"},
    {"method": "GET", "path": "/players/me", "task": "ST-102"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.player_repository = InMemoryPlayerRepository()
app.include_router(create_identity_router())
