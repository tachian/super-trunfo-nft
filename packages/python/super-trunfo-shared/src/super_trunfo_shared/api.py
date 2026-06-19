import logging
import os
from collections.abc import Iterable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .health import health_response
from .observability import (
    configure_json_logging,
    mask_sensitive_data,
    new_correlation_id,
    parse_json_body,
)
from .security import (
    FixedWindowRateLimiter,
    client_identifier,
    is_json_request,
    security_headers,
    security_settings_from_environment,
)

DEFAULT_CORS_ORIGINS = ""


def cors_origins_from_environment() -> list[str]:
    configured_origins = os.getenv("SUPER_TRUNFO_CORS_ORIGINS", DEFAULT_CORS_ORIGINS)

    return [
        origin.strip()
        for origin in configured_origins.split(",")
        if origin.strip()
    ]


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


def register_security_hardening(app: FastAPI) -> None:
    settings = security_settings_from_environment()
    rate_limiter = FixedWindowRateLimiter(
        limit=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )

    @app.middleware("http")
    async def harden_http_request(request: Request, call_next) -> Response:
        body = await request.body()

        async def receive() -> dict[str, object]:
            return {"type": "http.request", "body": body, "more_body": False}

        if len(body) > settings.max_request_body_bytes:
            response = JSONResponse(
                status_code=413,
                content={"detail": "Request body is too large."},
            )
            apply_security_headers(response, hsts_enabled=settings.hsts_enabled)
            return response

        if not is_json_request(request, body):
            response = JSONResponse(
                status_code=415,
                content={"detail": "Unsupported media type."},
            )
            apply_security_headers(response, hsts_enabled=settings.hsts_enabled)
            return response

        if should_rate_limit(request, settings.excluded_paths, settings.rate_limit_enabled):
            decision = rate_limiter.check(
                f"{client_identifier(request)}:{request.method}:{request.url.path}"
            )

            if not decision.allowed:
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests."},
                    headers={
                        "retry-after": str(decision.reset_seconds),
                        "x-ratelimit-limit": str(decision.limit),
                        "x-ratelimit-remaining": str(decision.remaining),
                        "x-ratelimit-reset": str(decision.reset_seconds),
                    },
                )
                apply_security_headers(response, hsts_enabled=settings.hsts_enabled)
                return response

        response = await call_next(Request(request.scope, receive))
        apply_security_headers(response, hsts_enabled=settings.hsts_enabled)

        return response


def should_rate_limit(
    request: Request,
    excluded_paths: tuple[str, ...],
    enabled: bool,
) -> bool:
    if not enabled:
        return False

    if request.method == "OPTIONS":
        return False

    return request.url.path not in excluded_paths


def apply_security_headers(response: Response, *, hsts_enabled: bool) -> None:
    for header, value in security_headers(hsts_enabled=hsts_enabled).items():
        response.headers.setdefault(header, value)


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
    app.add_middleware(
        CORSMiddleware,
        allow_headers=["authorization", "content-type", "x-correlation-id"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_origins=cors_origins_from_environment(),
    )
    register_security_hardening(app)
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
