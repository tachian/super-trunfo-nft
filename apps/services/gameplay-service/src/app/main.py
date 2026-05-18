from fastapi import status
from super_trunfo_shared.api import create_service_app

SERVICE_NAME = "gameplay-service"
CONTEXT = "gameplay"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/match/{id}", "task": "ST-302"},
    {"method": "POST", "path": "/match/{id}/play", "task": "ST-305"},
    {"method": "GET", "path": "/match/{id}/replay", "task": "ST-304"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)


@app.get("/match/{match_id}", status_code=status.HTTP_202_ACCEPTED, tags=["gameplay"])
async def get_match(match_id: str) -> dict[str, str]:
    return {"service": SERVICE_NAME, "match_id": match_id, "status": "planned", "task": "ST-302"}


@app.post("/match/{match_id}/play", status_code=status.HTTP_202_ACCEPTED, tags=["gameplay"])
async def play_round(match_id: str) -> dict[str, str]:
    return {"service": SERVICE_NAME, "match_id": match_id, "status": "planned", "task": "ST-305"}


@app.get("/match/{match_id}/replay", status_code=status.HTTP_202_ACCEPTED, tags=["gameplay"])
async def match_replay(match_id: str) -> dict[str, str]:
    return {"service": SERVICE_NAME, "match_id": match_id, "status": "planned", "task": "ST-304"}

