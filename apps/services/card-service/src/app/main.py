from super_trunfo_shared.api import create_service_app

from app.api.routes import create_cards_router

SERVICE_NAME = "card-service"
CONTEXT = "cards"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/cards", "task": "ST-201"},
    {"method": "GET", "path": "/cards/{id}", "task": "ST-201"},
    {"method": "POST", "path": "/cards/select-deck", "task": "ST-301"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.include_router(create_cards_router())
