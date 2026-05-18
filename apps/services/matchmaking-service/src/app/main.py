from fastapi import status
from super_trunfo_shared.api import create_service_app

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


@app.post("/matchmaking/find", status_code=status.HTTP_202_ACCEPTED, tags=["matchmaking"])
async def find_match() -> dict[str, str]:
    return {
        "service": SERVICE_NAME,
        "status": "planned",
        "task": "ST-402",
        "fallback": "pve-bot",
    }


@app.get("/matchmaking/queues", status_code=status.HTTP_202_ACCEPTED, tags=["matchmaking"])
async def matchmaking_queues() -> dict[str, object]:
    return {
        "service": SERVICE_NAME,
        "status": "planned",
        "task": "ST-401",
        "queues": ["queue:bronze", "queue:silver", "queue:gold"],
    }

