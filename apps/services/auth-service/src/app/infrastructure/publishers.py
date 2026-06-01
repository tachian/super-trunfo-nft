import logging
from threading import Lock

from super_trunfo_shared import DomainEvent
from super_trunfo_shared.observability import mask_sensitive_data, new_correlation_id


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
            extra={
                "service": self._service_name,
                "context": self._context,
                "correlation_id": correlation_id,
                "event": "domain.event.publish.requested",
                "method": "PUBLISH",
                "path": event.name,
                "status_code": "",
                "destination": "in-memory-domain-event-bus",
                "domain_event_name": event.name,
                "domain_event_id": event.event_id,
                "aggregate_id": event.aggregate_id,
                "event_payload": event_payload,
            },
        )

        with self._lock:
            self._events.append(event)

        self._logger.info(
            "domain event publish completed",
            extra={
                "service": self._service_name,
                "context": self._context,
                "correlation_id": correlation_id,
                "event": "domain.event.publish.completed",
                "method": "PUBLISH",
                "path": event.name,
                "status_code": "accepted",
                "destination": "in-memory-domain-event-bus",
                "domain_event_name": event.name,
                "domain_event_id": event.event_id,
                "aggregate_id": event.aggregate_id,
                "event_payload": event_payload,
            },
        )

    def published_events(self) -> tuple[DomainEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
