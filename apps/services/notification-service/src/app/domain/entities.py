from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .exceptions import NotificationInvariantError, UnsupportedNotificationEventError


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    PUSH = "push"


class NotificationTopic(StrEnum):
    INVITE = "invite"
    MATCH = "match"
    SHOP = "shop"
    RANKING = "ranking"
    EVENT = "event"


class NotificationStatus(StrEnum):
    QUEUED = "queued"
    DELIVERED = "delivered"


@dataclass(frozen=True)
class Notification:
    id: UUID
    player_id: UUID
    topic: NotificationTopic
    channel: NotificationChannel
    title: str
    message: str
    status: NotificationStatus
    created_at: datetime
    delivered_at: datetime | None = None
    source_event_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_topic = NotificationTopic(self.topic)
        normalized_channel = NotificationChannel(self.channel)
        normalized_status = NotificationStatus(self.status)
        title = self.title.strip()
        message = self.message.strip()
        metadata = normalize_metadata(self.metadata)

        if not title:
            raise NotificationInvariantError("notification title is required")

        if not message:
            raise NotificationInvariantError("notification message is required")

        if self.created_at.tzinfo is None:
            raise NotificationInvariantError("notification creation date must be timezone-aware")

        if self.delivered_at is not None and self.delivered_at.tzinfo is None:
            raise NotificationInvariantError("notification delivery date must be timezone-aware")

        if normalized_status == NotificationStatus.QUEUED and self.delivered_at is not None:
            raise NotificationInvariantError("queued notification cannot include delivery date")

        if normalized_status == NotificationStatus.DELIVERED and self.delivered_at is None:
            raise NotificationInvariantError("delivered notification requires delivery date")

        object.__setattr__(self, "topic", normalized_topic)
        object.__setattr__(self, "channel", normalized_channel)
        object.__setattr__(self, "status", normalized_status)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "message", message)
        object.__setattr__(self, "metadata", metadata)

    def mark_delivered(
        self,
        *,
        delivered_at: datetime | None = None,
    ) -> "Notification":
        if self.status != NotificationStatus.QUEUED:
            raise NotificationInvariantError("only queued notifications can be delivered")

        return Notification(
            id=self.id,
            player_id=self.player_id,
            topic=self.topic,
            channel=self.channel,
            title=self.title,
            message=self.message,
            status=NotificationStatus.DELIVERED,
            created_at=self.created_at,
            delivered_at=delivered_at or datetime.now(UTC),
            source_event_id=self.source_event_id,
            metadata=self.metadata,
        )


def queue_notification(
    *,
    player_id: UUID,
    topic: NotificationTopic,
    channel: NotificationChannel,
    title: str,
    message: str,
    notification_id: UUID | None = None,
    created_at: datetime | None = None,
    source_event_id: str | None = None,
    metadata: dict[str, str] | None = None,
) -> Notification:
    return Notification(
        id=notification_id or uuid4(),
        player_id=player_id,
        topic=topic,
        channel=channel,
        title=title,
        message=message,
        status=NotificationStatus.QUEUED,
        created_at=created_at or datetime.now(UTC),
        source_event_id=source_event_id,
        metadata=metadata or {},
    )


def notification_from_external_event(
    *,
    name: str,
    payload: dict[str, object],
    event_id: str | None = None,
    channel: NotificationChannel = NotificationChannel.IN_APP,
) -> Notification:
    template = notification_template(name, payload)
    player_id = extract_player_id(payload, template.player_id_field)

    return queue_notification(
        player_id=player_id,
        topic=template.topic,
        channel=channel,
        title=template.title,
        message=template.message,
        source_event_id=event_id,
        metadata={"event_name": name, "source": template.source},
    )


@dataclass(frozen=True)
class NotificationTemplate:
    topic: NotificationTopic
    player_id_field: str
    title: str
    message: str
    source: str


def notification_template(name: str, payload: dict[str, object]) -> NotificationTemplate:
    if name == "FriendInviteSent":
        return NotificationTemplate(
            topic=NotificationTopic.INVITE,
            player_id_field="addressee_id",
            title="Novo convite de amizade",
            message="Voce recebeu um convite de amizade.",
            source="social-service",
        )

    if name in {"FriendInviteAccepted", "FriendInviteRejected"}:
        action = "aceito" if name == "FriendInviteAccepted" else "recusado"
        return NotificationTemplate(
            topic=NotificationTopic.INVITE,
            player_id_field="requester_id",
            title="Convite de amizade respondido",
            message=f"Seu convite de amizade foi {action}.",
            source="social-service",
        )

    if name in {"MatchStarted", "BotMatchCreated"}:
        return NotificationTemplate(
            topic=NotificationTopic.MATCH,
            player_id_field="player_id",
            title="Partida encontrada",
            message="Sua partida esta pronta para jogar.",
            source="matchmaking-service",
        )

    if name in {"MatchResultUpdated", "PlayerWonMatch", "RoundFinished"}:
        return NotificationTemplate(
            topic=NotificationTopic.MATCH,
            player_id_field=match_player_field(name, payload),
            title="Resultado de partida atualizado",
            message="Sua partida recebeu uma nova atualizacao.",
            source="gameplay-service",
        )

    if name in {"CreditsEarned", "OfferPurchased"}:
        return NotificationTemplate(
            topic=NotificationTopic.SHOP,
            player_id_field="player_id",
            title="Loja e creditos atualizados",
            message="Sua economia no jogo recebeu uma atualizacao.",
            source="economy-service",
        )

    if name == "PlayerRankUpdated":
        return NotificationTemplate(
            topic=NotificationTopic.RANKING,
            player_id_field="player_id",
            title="Ranking atualizado",
            message="Sua posicao no ranking foi atualizada.",
            source="ranking-service",
        )

    if name in {"MarketplaceListingCreated", "TradeCreated", "TradeAccepted", "TradeCancelled"}:
        return NotificationTemplate(
            topic=NotificationTopic.SHOP,
            player_id_field=marketplace_player_field(name),
            title="Marketplace atualizado",
            message="Seu marketplace recebeu uma atualizacao.",
            source="nft-service",
        )

    if "player_id" in payload:
        return NotificationTemplate(
            topic=NotificationTopic.EVENT,
            player_id_field="player_id",
            title="Novo evento",
            message="Um evento importante foi registrado na sua conta.",
            source="platform",
        )

    raise UnsupportedNotificationEventError("event does not include a notification recipient")


def match_player_field(name: str, payload: dict[str, object]) -> str:
    if name == "PlayerWonMatch":
        return "winner_id"

    if payload.get("winner_id") is not None:
        return "winner_id"

    return "player_id"


def marketplace_player_field(name: str) -> str:
    if name == "TradeCreated":
        return "seller_id"

    if name == "TradeAccepted":
        return "buyer_id"

    return "seller_id"


def extract_player_id(payload: dict[str, object], field_name: str) -> UUID:
    value = payload.get(field_name)

    if value is None:
        raise UnsupportedNotificationEventError("event does not include a notification recipient")

    try:
        return UUID(str(value))
    except ValueError as exc:
        raise UnsupportedNotificationEventError("event recipient must be a UUID") from exc


def normalize_metadata(metadata: dict[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}

    for key, value in metadata.items():
        normalized_key = str(key).strip()
        normalized_value = str(value).strip()

        if not normalized_key:
            raise NotificationInvariantError("notification metadata keys are required")

        normalized[normalized_key] = normalized_value

    return normalized
