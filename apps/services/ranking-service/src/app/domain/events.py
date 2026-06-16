from super_trunfo_shared import DomainEvent

from .entities import Rating


def player_rank_updated_event(
    *,
    match_id: str,
    rating: Rating,
    previous_score: int,
) -> DomainEvent:
    return DomainEvent(
        name="PlayerRankUpdated",
        aggregate_id=str(rating.player_id),
        occurred_at=rating.updated_at,
        payload={
            "schema_version": "1.0.0",
            "match_id": match_id,
            "player_id": str(rating.player_id),
            "previous_score": previous_score,
            "score": rating.score,
            "delta": rating.score - previous_score,
            "tier": rating.tier.value,
            "matches_played": rating.matches_played,
            "wins": rating.wins,
            "losses": rating.losses,
            "updated_at": rating.updated_at.isoformat() if rating.updated_at else None,
        },
    )
