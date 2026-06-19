from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.application.use_cases import (
    ListNotifications,
    ListNotificationsQuery,
    MarkNotificationDelivered,
    MarkNotificationDeliveredCommand,
    QueueNotification,
    QueueNotificationCommand,
    QueueNotificationFromEvent,
    QueueNotificationFromEventCommand,
)
from app.domain.entities import Notification, NotificationChannel, NotificationTopic
from app.domain.exceptions import (
    NotificationInvariantError,
    NotificationNotFoundError,
    UnsupportedNotificationEventError,
)


class QueueNotificationRequest(BaseModel):
    player_id: UUID
    topic: NotificationTopic
    channel: NotificationChannel = NotificationChannel.IN_APP
    title: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=500)
    source_event_id: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class QueueNotificationFromEventRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    payload: dict[str, object]
    event_id: str | None = None
    channel: NotificationChannel = NotificationChannel.IN_APP


class NotificationEventResponse(BaseModel):
    name: str
    aggregate_id: str
    payload: dict[str, object]
    occurred_at: datetime
    event_id: str


class NotificationResponse(BaseModel):
    id: UUID
    player_id: UUID
    topic: str
    channel: str
    title: str
    message: str
    status: str
    created_at: datetime
    delivered_at: datetime | None
    source_event_id: str | None
    metadata: dict[str, str]


class NotificationActionResponse(BaseModel):
    service: str
    task: str
    notification: NotificationResponse
    events: list[NotificationEventResponse]


class NotificationsResponse(BaseModel):
    service: str
    task: str
    player_id: UUID
    notifications: list[NotificationResponse]


def create_notification_router() -> APIRouter:
    router = APIRouter(tags=["notification"])

    @router.get(
        "/notifications",
        operation_id="listNotifications",
        response_model=NotificationsResponse,
    )
    async def notifications(
        request: Request,
        player_id: Annotated[UUID, Query()],
    ) -> NotificationsResponse:
        result = ListNotifications(request.app.state.notification_repository).execute(
            ListNotificationsQuery(player_id=player_id)
        )

        return NotificationsResponse(
            service="notification-service",
            task="ST-802",
            player_id=result.player_id,
            notifications=[
                notification_response(notification)
                for notification in result.notifications
            ],
        )

    @router.post(
        "/notifications/push",
        operation_id="queueNotification",
        response_model=NotificationActionResponse,
        status_code=status.HTTP_201_CREATED,
        responses={400: {"description": "Invalid notification"}},
    )
    async def push_notification(
        payload: QueueNotificationRequest,
        request: Request,
    ) -> NotificationActionResponse | JSONResponse:
        try:
            result = QueueNotification(
                request.app.state.notification_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                QueueNotificationCommand(
                    player_id=payload.player_id,
                    topic=payload.topic,
                    channel=payload.channel,
                    title=payload.title,
                    message=payload.message,
                    source_event_id=payload.source_event_id,
                    metadata=payload.metadata,
                )
            )
        except NotificationInvariantError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid notification."},
            )

        return notification_action_response(result.notification, result.events)

    @router.post(
        "/notifications/events",
        operation_id="queueNotificationFromEvent",
        response_model=NotificationActionResponse,
        status_code=status.HTTP_201_CREATED,
        responses={400: {"description": "Unsupported notification event"}},
    )
    async def consume_notification_event(
        payload: QueueNotificationFromEventRequest,
        request: Request,
    ) -> NotificationActionResponse | JSONResponse:
        try:
            result = QueueNotificationFromEvent(
                request.app.state.notification_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                QueueNotificationFromEventCommand(
                    name=payload.name,
                    payload=payload.payload,
                    event_id=payload.event_id,
                    channel=payload.channel,
                )
            )
        except UnsupportedNotificationEventError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Unsupported notification event."},
            )

        return notification_action_response(result.notification, result.events)

    @router.post(
        "/notifications/{notification_id}/delivered",
        operation_id="markNotificationDelivered",
        response_model=NotificationActionResponse,
        responses={
            400: {"description": "Notification cannot be delivered"},
            404: {"description": "Notification not found"},
        },
    )
    async def mark_notification_delivered(
        notification_id: UUID,
        request: Request,
    ) -> NotificationActionResponse | JSONResponse:
        try:
            result = MarkNotificationDelivered(
                request.app.state.notification_repository,
                request.app.state.domain_event_publisher,
            ).execute(MarkNotificationDeliveredCommand(notification_id=notification_id))
        except NotificationNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Notification not found."},
            )
        except NotificationInvariantError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Notification cannot be delivered."},
            )

        return notification_action_response(result.notification, result.events)

    return router


def notification_response(notification: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        player_id=notification.player_id,
        topic=notification.topic.value,
        channel=notification.channel.value,
        title=notification.title,
        message=notification.message,
        status=notification.status.value,
        created_at=notification.created_at,
        delivered_at=notification.delivered_at,
        source_event_id=notification.source_event_id,
        metadata=notification.metadata,
    )


def notification_action_response(
    notification: Notification,
    events,
) -> NotificationActionResponse:
    return NotificationActionResponse(
        service="notification-service",
        task="ST-802",
        notification=notification_response(notification),
        events=[notification_event_response(event) for event in events],
    )


def notification_event_response(event) -> NotificationEventResponse:
    return NotificationEventResponse(
        name=event.name,
        aggregate_id=event.aggregate_id,
        payload=event.payload,
        occurred_at=event.occurred_at,
        event_id=event.event_id,
    )
