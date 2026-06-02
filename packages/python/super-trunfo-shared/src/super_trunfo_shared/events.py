import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from uuid import uuid4

from .observability import mask_sensitive_data, new_correlation_id


@dataclass(frozen=True)
class DomainEvent:
    name: str
    aggregate_id: str
    payload: dict[str, object]
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_id: str = field(default_factory=lambda: str(uuid4()))


class InMemoryDomainEventPublisher:
    def __init__(self, *, service_name: str, context: str) -> None:
        self._events: list[DomainEvent] = []
        self._lock = Lock()
        self._logger = logging.getLogger(service_name)
        self._service_name = service_name
        self._context = context

    def publish(self, event: DomainEvent) -> None:
        correlation_id = new_correlation_id()
        event_payload = mask_sensitive_data(event.payload)

        self._logger.info(
            "domain event publish requested",
            extra=self._log_extra(
                event,
                correlation_id=correlation_id,
                event_payload=event_payload,
                status_code="",
                log_event="domain.event.publish.requested",
            ),
        )

        with self._lock:
            self._events.append(event)

        self._logger.info(
            "domain event publish completed",
            extra=self._log_extra(
                event,
                correlation_id=correlation_id,
                event_payload=event_payload,
                status_code="accepted",
                log_event="domain.event.publish.completed",
            ),
        )

    def published_events(self) -> tuple[DomainEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def _log_extra(
        self,
        event: DomainEvent,
        *,
        correlation_id: str,
        event_payload: dict[str, object],
        status_code: str,
        log_event: str,
    ) -> dict[str, object]:
        return {
            "service": self._service_name,
            "context": self._context,
            "correlation_id": correlation_id,
            "event": log_event,
            "method": "PUBLISH",
            "path": event.name,
            "status_code": status_code,
            "destination": "in-memory-domain-event-bus",
            "domain_event_name": event.name,
            "domain_event_id": event.event_id,
            "aggregate_id": event.aggregate_id,
            "event_payload": event_payload,
        }
