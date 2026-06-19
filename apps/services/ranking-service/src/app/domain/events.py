from super_trunfo_shared import DomainEvent

from .entities import Rating, Season, SeasonReward


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


def season_started_event(season: Season) -> DomainEvent:
    return DomainEvent(
        name="SeasonStarted",
        aggregate_id=str(season.id),
        occurred_at=season.starts_at,
        payload=season_payload(season),
    )


def season_finished_event(
    season: Season,
    *,
    reset_ratings_count: int,
) -> DomainEvent:
    return DomainEvent(
        name="SeasonFinished",
        aggregate_id=str(season.id),
        occurred_at=season.finished_at,
        payload={
            **season_payload(season),
            "reset_ratings_count": reset_ratings_count,
            "reward_plan": [season_reward_payload(reward) for reward in season.rewards],
        },
    )


def season_payload(season: Season) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "season_id": str(season.id),
        "name": season.name,
        "status": season.status.value,
        "starts_at": season.starts_at.isoformat(),
        "ends_at": season.ends_at.isoformat(),
        "duration_days": season.duration_days,
        "rating_reset_percentage": season.rating_reset_percentage,
        "finished_at": season.finished_at.isoformat()
        if season.finished_at is not None
        else None,
    }


def season_reward_payload(reward: SeasonReward) -> dict[str, object]:
    return {
        "player_id": str(reward.player_id),
        "position": reward.position,
        "tier": reward.tier.value,
        "planned_credits": reward.planned_credits,
        "planned_badge": reward.planned_badge,
    }
