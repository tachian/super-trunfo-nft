from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_notification_router
from app.infrastructure.repositories import InMemoryNotificationRepository

SERVICE_NAME = "notification-service"
CONTEXT = "notification"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/notifications", "task": "ST-802"},
    {"method": "POST", "path": "/notifications/push", "task": "ST-802"},
    {"method": "POST", "path": "/notifications/events", "task": "ST-802"},
    {"method": "POST", "path": "/notifications/{notification_id}/delivered", "task": "ST-802"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.notification_repository = InMemoryNotificationRepository()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.include_router(create_notification_router())
