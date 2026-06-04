from super_trunfo_shared.api import create_service_app

from app.api.routes import create_matchmaking_router
from app.application.use_cases import ConfigureTierQueues
from app.infrastructure.repositories import InMemoryMatchmakingQueueRepository

SERVICE_NAME = "matchmaking-service"
CONTEXT = "matchmaking"
PLANNED_ROUTES = [
    {"method": "POST", "path": "/matchmaking/find", "task": "ST-402"},
    {"method": "GET", "path": "/matchmaking/queues", "task": "ST-401"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.matchmaking_queue_repository = InMemoryMatchmakingQueueRepository()
ConfigureTierQueues(app.state.matchmaking_queue_repository).execute()
app.include_router(create_matchmaking_router())
