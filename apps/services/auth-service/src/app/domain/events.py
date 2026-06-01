from super_trunfo_shared import DomainEvent

from .entities import Player

AUTH_EVENT_SCHEMA_VERSION = "1.0.0"


def player_registered_event(player: Player) -> DomainEvent:
    onboarding = player.onboarding
    initial_deck_size = len(onboarding.initial_deck) if onboarding is not None else 0
    initial_credits = onboarding.initial_credits if onboarding is not None else 0

    return DomainEvent(
        name="PlayerRegistered",
        aggregate_id=str(player.id),
        payload={
            "schema_version": AUTH_EVENT_SCHEMA_VERSION,
            "player_id": str(player.id),
            "provider": player.social_login_provider,
            "rating": player.rating,
            "credits": player.credits,
            "initial_deck_size": initial_deck_size,
            "initial_credits": initial_credits,
        },
    )


def player_logged_in_event(player: Player) -> DomainEvent:
    return DomainEvent(
        name="PlayerLoggedIn",
        aggregate_id=str(player.id),
        payload={
            "schema_version": AUTH_EVENT_SCHEMA_VERSION,
            "player_id": str(player.id),
            "provider": player.social_login_provider,
        },
    )
