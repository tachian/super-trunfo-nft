from fastapi import status
from super_trunfo_shared.api import create_service_app
from super_trunfo_shared.cards import CardAttributes, calculate_card_level, card_uniqueness_hash

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


@app.get("/cards", status_code=status.HTTP_202_ACCEPTED, tags=["cards"])
async def list_cards() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-201"}


@app.post("/cards/select-deck", status_code=status.HTTP_202_ACCEPTED, tags=["cards"])
async def select_deck() -> dict[str, str]:
    return {"service": SERVICE_NAME, "status": "planned", "task": "ST-301"}


@app.get("/cards/{card_id}", status_code=status.HTTP_202_ACCEPTED, tags=["cards"])
async def get_card(card_id: str) -> dict[str, str]:
    return {"service": SERVICE_NAME, "card_id": card_id, "status": "planned", "task": "ST-201"}


@app.get("/cards/sample/hash", tags=["cards"])
async def sample_card_hash() -> dict[str, object]:
    attributes = CardAttributes(
        name="Shadow Titan",
        speed=82,
        strength=91,
        intelligence=64,
        resistance=76,
        rarity=80,
    )
    return {
        "level": calculate_card_level(attributes),
        "hash": card_uniqueness_hash(attributes),
    }

