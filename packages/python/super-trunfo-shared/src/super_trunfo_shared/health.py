from datetime import UTC, datetime


def health_response(*, service: str, context: str, status: str = "ok") -> dict[str, str]:
    return {
        "service": service,
        "context": context,
        "status": status,
        "checked_at": datetime.now(UTC).isoformat(),
    }

