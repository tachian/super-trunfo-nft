from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_economy_router
from app.infrastructure.repositories import InMemoryWalletRepository

SERVICE_NAME = "economy-service"
CONTEXT = "economy"
PLANNED_ROUTES = [
    {"method": "POST", "path": "/wallet/credits/match-result", "task": "ST-501"},
    {"method": "GET", "path": "/wallet/credits", "task": "ST-501"},
    {"method": "GET", "path": "/shop/offers", "task": "ST-502"},
    {"method": "POST", "path": "/shop/buy", "task": "ST-502"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.wallet_repository = InMemoryWalletRepository()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.include_router(create_economy_router())
