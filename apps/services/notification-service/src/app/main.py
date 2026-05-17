from fastapi import status

from super_trunfo_shared.api import create_service_app

SERVICE_NAME = "notification-service"
CONTEXT = "notification"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/notifications", "task": "ST-802"},
    {"method": "POST", "path": "/notifications/push", "task": "ST-802"},
    {"method": "POST", "path": "/notifications/events", "task": "ST-802"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)


@app.get("/notifications", status_code=status.HTTP_202_ACCEPTED, tags=["notification"])
async def notifications() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-802"}


@app.post("/notifications/push", status_code=status.HTTP_202_ACCEPTED, tags=["notification"])
async def push_notification() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-802"}


@app.post("/notifications/events", status_code=status.HTTP_202_ACCEPTED, tags=["notification"])
async def consume_notification_event() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-802"}

