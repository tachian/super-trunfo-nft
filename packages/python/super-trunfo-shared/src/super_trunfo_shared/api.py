from collections.abc import Iterable

from fastapi import FastAPI

from .health import health_response


def create_service_app(
    *,
    service_name: str,
    context: str,
    planned_routes: Iterable[dict[str, str]],
) -> FastAPI:
    app = FastAPI(
        title=service_name,
        version="0.1.0",
        description=f"{service_name} handles the {context} bounded context.",
    )

    @app.get("/health", tags=["platform"])
    async def health() -> dict[str, str]:
        return health_response(service=service_name, context=context)

    @app.get("/ready", tags=["platform"])
    async def ready() -> dict[str, str]:
        return health_response(service=service_name, context=context, status="ready")

    @app.get("/context", tags=["platform"])
    async def context_info() -> dict[str, object]:
        return {
            "service": service_name,
            "context": context,
            "planned_routes": list(planned_routes),
        }

    return app

