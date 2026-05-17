from fastapi import status

from super_trunfo_shared.api import create_service_app

SERVICE_NAME = "economy-service"
CONTEXT = "economy"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/shop/offers", "task": "ST-502"},
    {"method": "POST", "path": "/shop/buy", "task": "ST-502"},
    {"method": "GET", "path": "/wallet/credits", "task": "ST-501"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)


@app.get("/shop/offers", status_code=status.HTTP_202_ACCEPTED, tags=["economy"])
async def shop_offers() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-502"}


@app.post("/shop/buy", status_code=status.HTTP_202_ACCEPTED, tags=["economy"])
async def buy_offer() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-502"}


@app.get("/wallet/credits", status_code=status.HTTP_202_ACCEPTED, tags=["economy"])
async def wallet_credits() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-501"}

