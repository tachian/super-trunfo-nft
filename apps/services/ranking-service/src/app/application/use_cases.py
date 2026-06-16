from dataclasses import dataclass
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import Rating, create_rating, recalculate_elo_ratings
from app.domain.events import player_rank_updated_event
from app.domain.repositories import DomainEventPublisher, RatingRepository


@dataclass(frozen=True)
class RecalculatePlayerRatingCommand:
    match_id: UUID
    winner_id: UUID
    loser_id: UUID


@dataclass(frozen=True)
class RecalculatePlayerRatingResult:
    winner_rating: Rating
    loser_rating: Rating
    created: bool
    events: tuple[DomainEvent, ...]


class RecalculatePlayerRating:
    def __init__(
        self,
        rating_repository: RatingRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.rating_repository = rating_repository
        self.event_publisher = event_publisher

    def execute(
        self,
        command: RecalculatePlayerRatingCommand,
    ) -> RecalculatePlayerRatingResult:
        winner = self.rating_repository.find_by_player_id(
            command.winner_id
        ) or create_rating(command.winner_id)
        loser = self.rating_repository.find_by_player_id(
            command.loser_id
        ) or create_rating(command.loser_id)
        previous_winner_score = winner.score
        previous_loser_score = loser.score

        updated_winner, updated_loser, created = recalculate_elo_ratings(
            winner=winner,
            loser=loser,
            match_id=command.match_id,
        )

        if not created:
            return RecalculatePlayerRatingResult(
                winner_rating=updated_winner,
                loser_rating=updated_loser,
                created=False,
                events=(),
            )

        self.rating_repository.save_many((updated_winner, updated_loser))
        events = (
            player_rank_updated_event(
                match_id=str(command.match_id),
                rating=updated_winner,
                previous_score=previous_winner_score,
            ),
            player_rank_updated_event(
                match_id=str(command.match_id),
                rating=updated_loser,
                previous_score=previous_loser_score,
            ),
        )

        for event in events:
            self.event_publisher.publish(event)

        return RecalculatePlayerRatingResult(
            winner_rating=updated_winner,
            loser_rating=updated_loser,
            created=True,
            events=events,
        )
