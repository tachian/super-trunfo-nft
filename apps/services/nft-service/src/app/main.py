from fastapi import status

from super_trunfo_shared.api import create_service_app

SERVICE_NAME = "nft-service"
CONTEXT = "nft"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/nft/metadata/{card_id}", "task": "ST-205"},
    {"method": "POST", "path": "/nft/mint", "task": "ST-701"},
    {"method": "GET", "path": "/marketplace/listings", "task": "ST-703"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)


@app.get("/nft/metadata/{card_id}", status_code=status.HTTP_202_ACCEPTED, tags=["nft"])
async def nft_metadata(card_id: str) -> dict[str, str]:
    return {"service": SERVICE_NAME, "card_id": card_id, "status": "planned", "task": "ST-205"}


@app.post("/nft/mint", status_code=status.HTTP_202_ACCEPTED, tags=["nft"])
async def mint_nft() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-701"}


@app.get("/marketplace/listings", status_code=status.HTTP_202_ACCEPTED, tags=["marketplace"])
async def marketplace_listings() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-703"}

