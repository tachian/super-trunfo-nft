from fastapi import status
from super_trunfo_shared.api import create_service_app

SERVICE_NAME = "social-service"
CONTEXT = "social"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/friends", "task": "ST-801"},
    {"method": "POST", "path": "/friends/invite", "task": "ST-801"},
    {"method": "GET", "path": "/guilds", "task": "ST-803"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)


@app.get("/friends", status_code=status.HTTP_202_ACCEPTED, tags=["social"])
async def friends() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-801"}


@app.post("/friends/invite", status_code=status.HTTP_202_ACCEPTED, tags=["social"])
async def invite_friend() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-801"}


@app.get("/guilds", status_code=status.HTTP_202_ACCEPTED, tags=["social"])
async def guilds() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-803"}

