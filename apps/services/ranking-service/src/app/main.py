from fastapi import status

from super_trunfo_shared.api import create_service_app

SERVICE_NAME = "ranking-service"
CONTEXT = "ranking"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/ranking/global", "task": "ST-504"},
    {"method": "GET", "path": "/ranking/friends", "task": "ST-504"},
    {"method": "POST", "path": "/ranking/recalculate", "task": "ST-503"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)


@app.get("/ranking/global", status_code=status.HTTP_202_ACCEPTED, tags=["ranking"])
async def global_ranking() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-504"}


@app.get("/ranking/friends", status_code=status.HTTP_202_ACCEPTED, tags=["ranking"])
async def friends_ranking() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-504"}


@app.post("/ranking/recalculate", status_code=status.HTTP_202_ACCEPTED, tags=["ranking"])
async def recalculate_ranking() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-503"}

