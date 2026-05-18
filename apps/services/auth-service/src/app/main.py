from fastapi import status
from super_trunfo_shared.api import create_service_app

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


@app.post("/auth/register", status_code=status.HTTP_202_ACCEPTED, tags=["identity"])
async def register_player() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-101"}


@app.post("/auth/login", status_code=status.HTTP_202_ACCEPTED, tags=["identity"])
async def login_player() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-101"}


@app.get("/players/me", status_code=status.HTTP_202_ACCEPTED, tags=["identity"])
async def current_player_profile() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-102"}

