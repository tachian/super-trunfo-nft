from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.entities import (
    LEVEL_TOLERANCE,
    MatchmakingMatch,
    MatchmakingTicket,
    MatchStartedEvent,
    TierQueue,
    configured_tier_queues,
    create_pve_match,
    create_pvp_match,
    match_started_event,
    queue_name_for_tier,
    tier_for_average_level,
)
from app.domain.repositories import (
    MatchmakingEventPublisher,
    MatchmakingQueueRepository,
    QueueStatus,
)


@dataclass(frozen=True)
class GetQueueStatusResult:
    queues: tuple[QueueStatus, ...]


@dataclass(frozen=True)
class RequestMatchCommand:
    player_id: UUID
    average_deck_level: int
    fallback_after_seconds: int = 0
    ticket_id: UUID | None = None


@dataclass(frozen=True)
class RequestMatchResult:
    ticket: MatchmakingTicket
    status: str
    matched_ticket: MatchmakingTicket | None = None
    match: MatchmakingMatch | None = None
    events: tuple[MatchStartedEvent, ...] = ()
    tolerance: int = LEVEL_TOLERANCE
    fallback_after_seconds: int = 0

    @property
    def ticket_queue(self) -> TierQueue:
        return TierQueue(
            tier=self.ticket.tier,
            name=queue_name_for_tier(self.ticket.tier),
        )


class ConfigureTierQueues:
    def __init__(self, repository: MatchmakingQueueRepository) -> None:
        self.repository = repository

    def execute(self) -> tuple[TierQueue, ...]:
        queues = configured_tier_queues()
        self.repository.ensure_queues(queues)

        return queues


class GetQueueStatus:
    def __init__(self, repository: MatchmakingQueueRepository) -> None:
        self.repository = repository

    def execute(self) -> GetQueueStatusResult:
        queues = configured_tier_queues()
        self.repository.ensure_queues(queues)

        return GetQueueStatusResult(
            queues=tuple(
                QueueStatus(
                    queue=queue,
                    size=self.repository.queue_size(queue),
                )
                for queue in queues
            )
        )


class RequestMatch:
    def __init__(
        self,
        repository: MatchmakingQueueRepository,
        event_publisher: MatchmakingEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: RequestMatchCommand) -> RequestMatchResult:
        if command.fallback_after_seconds < 0:
            raise ValueError("fallback_after_seconds cannot be negative")

        ticket = MatchmakingTicket(
            id=command.ticket_id or uuid4(),
            player_id=command.player_id,
            average_deck_level=command.average_deck_level,
            tier=tier_for_average_level(command.average_deck_level),
        )
        self.repository.ensure_queues(configured_tier_queues())
        matched_ticket = self.repository.find_compatible_ticket(
            ticket,
            tolerance=LEVEL_TOLERANCE,
        )

        if matched_ticket is not None:
            match = create_pvp_match(ticket=ticket, opponent_ticket=matched_ticket)
            event = match_started_event(match)
            self.event_publisher.publish(event)

            return RequestMatchResult(
                ticket=ticket,
                status="matched",
                matched_ticket=matched_ticket,
                match=match,
                events=(event,),
                fallback_after_seconds=command.fallback_after_seconds,
            )

        if command.fallback_after_seconds == 0:
            match = create_pve_match(ticket=ticket)
            event = match_started_event(match)
            self.event_publisher.publish(event)

            return RequestMatchResult(
                ticket=ticket,
                status="pve_created",
                match=match,
                events=(event,),
                fallback_after_seconds=command.fallback_after_seconds,
            )

        self.repository.enqueue_ticket(ticket)

        return RequestMatchResult(
            ticket=ticket,
            status="queued",
            fallback_after_seconds=command.fallback_after_seconds,
        )
