from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.application.use_cases import (
    AcceptFriendInvite,
    AnswerFriendInviteCommand,
    ListFriends,
    ListFriendsQuery,
    RejectFriendInvite,
    SendFriendInvite,
    SendFriendInviteCommand,
)
from app.domain.entities import FriendInvite, Friendship
from app.domain.exceptions import FriendInviteNotFoundError, SocialInvariantError


class SendFriendInviteRequest(BaseModel):
    requester_id: UUID
    addressee_id: UUID


class AnswerFriendInviteRequest(BaseModel):
    player_id: UUID


class SocialEventResponse(BaseModel):
    name: str
    aggregate_id: str
    payload: dict[str, object]
    occurred_at: datetime
    event_id: str


class FriendInviteResponse(BaseModel):
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: str
    created_at: datetime
    responded_at: datetime | None


class FriendshipResponse(BaseModel):
    id: UUID
    player_id: UUID
    friend_id: UUID
    created_at: datetime


class FriendInviteActionResponse(BaseModel):
    service: str
    task: str
    invite: FriendInviteResponse
    friendship: FriendshipResponse | None
    events: list[SocialEventResponse]


class FriendsResponse(BaseModel):
    service: str
    task: str
    player_id: UUID
    friends: list[FriendshipResponse]


def create_social_router() -> APIRouter:
    router = APIRouter(tags=["social"])

    @router.get(
        "/friends",
        operation_id="listFriends",
        response_model=FriendsResponse,
    )
    async def friends(
        request: Request,
        player_id: Annotated[UUID, Query()],
    ) -> FriendsResponse:
        result = ListFriends(request.app.state.social_repository).execute(
            ListFriendsQuery(player_id=player_id)
        )

        return FriendsResponse(
            service="social-service",
            task="ST-801",
            player_id=result.player_id,
            friends=[
                friendship_response(friendship, player_id=result.player_id)
                for friendship in result.friendships
            ],
        )

    @router.post(
        "/friends/invite",
        operation_id="sendFriendInvite",
        response_model=FriendInviteActionResponse,
        status_code=status.HTTP_201_CREATED,
        responses={400: {"description": "Invalid friend invite"}},
    )
    async def invite_friend(
        payload: SendFriendInviteRequest,
        request: Request,
    ) -> FriendInviteActionResponse | JSONResponse:
        try:
            result = SendFriendInvite(
                request.app.state.social_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                SendFriendInviteCommand(
                    requester_id=payload.requester_id,
                    addressee_id=payload.addressee_id,
                )
            )
        except SocialInvariantError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid friend invite."},
            )

        return friend_invite_action_response(result.invite, None, result.events)

    @router.post(
        "/friends/invite/{invite_id}/accept",
        operation_id="acceptFriendInvite",
        response_model=FriendInviteActionResponse,
        responses={
            400: {"description": "Friend invite cannot be accepted"},
            404: {"description": "Friend invite not found"},
        },
    )
    async def accept_friend_invite(
        invite_id: UUID,
        payload: AnswerFriendInviteRequest,
        request: Request,
    ) -> FriendInviteActionResponse | JSONResponse:
        try:
            result = AcceptFriendInvite(
                request.app.state.social_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                AnswerFriendInviteCommand(
                    invite_id=invite_id,
                    player_id=payload.player_id,
                )
            )
        except FriendInviteNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Friend invite not found."},
            )
        except SocialInvariantError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Friend invite cannot be accepted."},
            )

        return friend_invite_action_response(result.invite, result.friendship, result.events)

    @router.post(
        "/friends/invite/{invite_id}/reject",
        operation_id="rejectFriendInvite",
        response_model=FriendInviteActionResponse,
        responses={
            400: {"description": "Friend invite cannot be rejected"},
            404: {"description": "Friend invite not found"},
        },
    )
    async def reject_friend_invite(
        invite_id: UUID,
        payload: AnswerFriendInviteRequest,
        request: Request,
    ) -> FriendInviteActionResponse | JSONResponse:
        try:
            result = RejectFriendInvite(
                request.app.state.social_repository,
                request.app.state.domain_event_publisher,
            ).execute(
                AnswerFriendInviteCommand(
                    invite_id=invite_id,
                    player_id=payload.player_id,
                )
            )
        except FriendInviteNotFoundError:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "Friend invite not found."},
            )
        except SocialInvariantError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Friend invite cannot be rejected."},
            )

        return friend_invite_action_response(result.invite, None, result.events)

    @router.get("/guilds", status_code=status.HTTP_202_ACCEPTED)
    async def guilds() -> dict[str, str]:
        return {"service": "social-service", "status": "planned", "task": "ST-803"}

    return router


def friend_invite_response(invite: FriendInvite) -> FriendInviteResponse:
    return FriendInviteResponse(
        id=invite.id,
        requester_id=invite.requester_id,
        addressee_id=invite.addressee_id,
        status=invite.status.value,
        created_at=invite.created_at,
        responded_at=invite.responded_at,
    )


def friendship_response(friendship: Friendship, *, player_id: UUID) -> FriendshipResponse:
    return FriendshipResponse(
        id=friendship.id,
        player_id=player_id,
        friend_id=friendship.friend_id_for(player_id),
        created_at=friendship.created_at,
    )


def friend_invite_action_response(
    invite: FriendInvite,
    friendship: Friendship | None,
    events,
) -> FriendInviteActionResponse:
    return FriendInviteActionResponse(
        service="social-service",
        task="ST-801",
        invite=friend_invite_response(invite),
        friendship=friendship_response(friendship, player_id=invite.addressee_id)
        if friendship is not None
        else None,
        events=[
            SocialEventResponse(
                name=event.name,
                aggregate_id=event.aggregate_id,
                payload=event.payload,
                occurred_at=event.occurred_at,
                event_id=event.event_id,
            )
            for event in events
        ],
    )
