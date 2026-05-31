import logging
from collections.abc import Iterable

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from .health import health_response
from .observability import (
    configure_json_logging,
    mask_sensitive_data,
    new_correlation_id,
    parse_json_body,
)


def register_request_logging(app: FastAPI, *, service_name: str, context: str) -> None:
    logger = logging.getLogger(service_name)

    @app.middleware("http")
    async def log_http_request(request: Request, call_next) -> Response:
        correlation_id = request.headers.get("x-correlation-id", new_correlation_id())
        body = await request.body()
        request_payload = mask_sensitive_data(parse_json_body(body))

        async def receive() -> dict[str, object]:
            return {"type": "http.request", "body": body, "more_body": False}

        logger.info(
            "external request received",
            extra={
                "service": service_name,
                "context": context,
                "correlation_id": correlation_id,
                "event": "http.request.received",
                "method": request.method,
                "path": request.url.path,
                "query_params": mask_sensitive_data(dict(request.query_params)),
                "request_body": request_payload,
            },
        )

        response = await call_next(Request(request.scope, receive))
        response_body = b"".join([chunk async for chunk in response.body_iterator])
        response_payload = mask_sensitive_data(parse_json_body(response_body))

        logger.info(
            "external request completed",
            extra={
                "service": service_name,
                "context": context,
                "correlation_id": correlation_id,
                "event": "http.response.sent",
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "response_body": response_payload,
            },
        )

        headers = dict(response.headers)
        headers["x-correlation-id"] = correlation_id

        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type,
            background=response.background,
        )


def create_service_app(
    *,
    service_name: str,
    context: str,
    planned_routes: Iterable[dict[str, str]],
) -> FastAPI:
    configure_json_logging()

    app = FastAPI(
        title=service_name,
        version="0.1.0",
        description=f"{service_name} handles the {context} bounded context.",
    )
    register_request_logging(app, service_name=service_name, context=context)

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
