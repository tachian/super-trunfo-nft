from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_nft_router
from app.infrastructure.repositories import (
    InMemoryMarketplaceListingRepository,
    InMemoryNftMetadataRepository,
)

SERVICE_NAME = "nft-service"
CONTEXT = "nft"
PLANNED_ROUTES = [
    {"method": "POST", "path": "/nft/metadata/offline", "task": "ST-205"},
    {"method": "GET", "path": "/nft/metadata/{card_id}", "task": "ST-205"},
    {"method": "POST", "path": "/nft/mint", "task": "ST-701"},
    {"method": "POST", "path": "/marketplace/listings", "task": "ST-703"},
    {"method": "GET", "path": "/marketplace/listings", "task": "ST-703"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.nft_metadata_repository = InMemoryNftMetadataRepository()
app.state.marketplace_listing_repository = InMemoryMarketplaceListingRepository()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.include_router(create_nft_router())
