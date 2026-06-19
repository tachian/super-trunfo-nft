import os
import time
from dataclasses import dataclass
from threading import Lock

from starlette.requests import Request

DEFAULT_RATE_LIMIT_REQUESTS = 120
DEFAULT_RATE_LIMIT_WINDOW_SECONDS = 60
DEFAULT_MAX_REQUEST_BODY_BYTES = 1024 * 1024
DEFAULT_EXCLUDED_PATHS = "/health,/ready,/context"


@dataclass(frozen=True)
class SecuritySettings:
    rate_limit_enabled: bool
    rate_limit_requests: int
    rate_limit_window_seconds: int
    max_request_body_bytes: int
    excluded_paths: tuple[str, ...]
    hsts_enabled: bool


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_seconds: int


class FixedWindowRateLimiter:
    def __init__(
        self,
        *,
        limit: int,
        window_seconds: int,
        now=time.monotonic,
    ) -> None:
        if limit < 1:
            raise ValueError("rate limit must be positive")

        if window_seconds < 1:
            raise ValueError("rate limit window must be positive")

        self._limit = limit
        self._window_seconds = window_seconds
        self._now = now
        self._lock = Lock()
        self._windows_by_key: dict[str, tuple[float, int]] = {}

    def check(self, key: str) -> RateLimitDecision:
        checked_at = self._now()

        with self._lock:
            window_start, count = self._windows_by_key.get(key, (checked_at, 0))

            if checked_at - window_start >= self._window_seconds:
                window_start = checked_at
                count = 0

            next_count = count + 1
            self._windows_by_key[key] = (window_start, next_count)
            reset_seconds = max(
                1,
                round(self._window_seconds - (checked_at - window_start)),
            )
            allowed = next_count <= self._limit
            remaining = max(0, self._limit - next_count)

        return RateLimitDecision(
            allowed=allowed,
            limit=self._limit,
            remaining=remaining,
            reset_seconds=reset_seconds,
        )


def security_settings_from_environment() -> SecuritySettings:
    return SecuritySettings(
        rate_limit_enabled=env_bool("SUPER_TRUNFO_RATE_LIMIT_ENABLED", default=True),
        rate_limit_requests=env_int(
            "SUPER_TRUNFO_RATE_LIMIT_REQUESTS",
            default=DEFAULT_RATE_LIMIT_REQUESTS,
        ),
        rate_limit_window_seconds=env_int(
            "SUPER_TRUNFO_RATE_LIMIT_WINDOW_SECONDS",
            default=DEFAULT_RATE_LIMIT_WINDOW_SECONDS,
        ),
        max_request_body_bytes=env_int(
            "SUPER_TRUNFO_MAX_REQUEST_BODY_BYTES",
            default=DEFAULT_MAX_REQUEST_BODY_BYTES,
        ),
        excluded_paths=env_tuple(
            "SUPER_TRUNFO_RATE_LIMIT_EXCLUDED_PATHS",
            default=DEFAULT_EXCLUDED_PATHS,
        ),
        hsts_enabled=env_bool("SUPER_TRUNFO_HSTS_ENABLED", default=False),
    )


def client_identifier(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    first_forwarded_ip = forwarded_for.split(",", maxsplit=1)[0].strip()

    if first_forwarded_ip:
        return first_forwarded_ip

    if request.client is None:
        return "unknown"

    return request.client.host


def is_json_request(request: Request, body: bytes) -> bool:
    if not body:
        return True

    if request.method not in {"POST", "PUT", "PATCH"}:
        return True

    content_type = request.headers.get("content-type", "")

    return content_type.startswith("application/json")


def security_headers(*, hsts_enabled: bool) -> dict[str, str]:
    headers = {
        "cache-control": "no-store",
        "permissions-policy": "geolocation=(), microphone=(), camera=()",
        "referrer-policy": "no-referrer",
        "x-content-type-options": "nosniff",
        "x-frame-options": "DENY",
    }

    if hsts_enabled:
        headers["strict-transport-security"] = "max-age=31536000; includeSubDomains"

    return headers


def env_bool(name: str, *, default: bool) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, *, default: int) -> int:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        return default

    return max(1, value)


def env_tuple(name: str, *, default: str) -> tuple[str, ...]:
    raw_value = os.getenv(name, default)

    return tuple(item.strip() for item in raw_value.split(",") if item.strip())
