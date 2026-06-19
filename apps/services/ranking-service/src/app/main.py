from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.api import create_service_app

from app.api.routes import create_ranking_router
from app.infrastructure.repositories import (
    InMemoryLeaderboardCache,
    InMemoryRatingRepository,
    InMemorySeasonRepository,
)

SERVICE_NAME = "ranking-service"
CONTEXT = "ranking"
PLANNED_ROUTES = [
    {"method": "GET", "path": "/ranking/global", "task": "ST-504"},
    {"method": "GET", "path": "/ranking/friends", "task": "ST-504"},
    {"method": "POST", "path": "/ranking/recalculate", "task": "ST-503"},
    {"method": "GET", "path": "/ranking/seasons/current", "task": "ST-803"},
    {"method": "POST", "path": "/ranking/seasons/start", "task": "ST-803"},
    {"method": "POST", "path": "/ranking/seasons/{season_id}/finish", "task": "ST-803"},
]

app = create_service_app(
    service_name=SERVICE_NAME,
    context=CONTEXT,
    planned_routes=PLANNED_ROUTES,
)
app.state.rating_repository = InMemoryRatingRepository()
app.state.season_repository = InMemorySeasonRepository()
app.state.leaderboard_cache = InMemoryLeaderboardCache()
app.state.domain_event_publisher = InMemoryDomainEventPublisher(
    service_name=SERVICE_NAME,
    context=CONTEXT,
)
app.include_router(create_ranking_router())
