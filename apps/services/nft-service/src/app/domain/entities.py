from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from urllib.parse import urlparse
from uuid import UUID, uuid4

from .exceptions import NftInvariantError

NftAttributeValue = int | str
NFT_IMAGE_BASE_URI = "ipfs://super-trunfo-nft/cards"


class MarketplaceListingStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SOLD = "sold"


@dataclass(frozen=True)
class NftAttribute:
    trait_type: str
    value: NftAttributeValue

    def __post_init__(self) -> None:
        normalized_trait = self.trait_type.strip()

        if not normalized_trait:
            raise NftInvariantError("NFT attribute trait type cannot be blank")

        object.__setattr__(self, "trait_type", normalized_trait)

    def to_erc721_json(self) -> dict[str, NftAttributeValue]:
        return {
            "trait_type": self.trait_type,
            "value": self.value,
        }


@dataclass(frozen=True)
class NftMetadata:
    card_id: UUID
    name: str
    description: str
    image: str
    attributes: tuple[NftAttribute, ...]
    generated_at: datetime
    mint_enabled: bool = False

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        normalized_description = self.description.strip()
        normalized_image = self.image.strip()

        if not normalized_name:
            raise NftInvariantError("NFT metadata name cannot be blank")

        if not normalized_description:
            raise NftInvariantError("NFT metadata description cannot be blank")

        if not normalized_image:
            raise NftInvariantError("NFT metadata image cannot be blank")

        if urlparse(normalized_image).scheme == "http":
            raise NftInvariantError("NFT metadata image must use a secure or decentralized URI")

        if not self.attributes:
            raise NftInvariantError("NFT metadata must include attributes")

        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "description", normalized_description)
        object.__setattr__(self, "image", normalized_image)

    @property
    def metadata_uri(self) -> str:
        return f"offline://super-trunfo-nft/metadata/{self.card_id}.json"

    def to_erc721_json(self) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "attributes": [attribute.to_erc721_json() for attribute in self.attributes],
            "properties": {
                "card_id": str(self.card_id),
                "metadata_uri": self.metadata_uri,
                "generated_at": self.generated_at.isoformat(),
                "mint_enabled": self.mint_enabled,
            },
        }


@dataclass(frozen=True)
class MarketplaceListingHistoryEntry:
    status: MarketplaceListingStatus
    changed_at: datetime
    reason: str

    def __post_init__(self) -> None:
        normalized_status = MarketplaceListingStatus(self.status)
        normalized_reason = self.reason.strip()

        if not normalized_reason:
            raise NftInvariantError("marketplace listing history reason cannot be blank")

        if self.changed_at.tzinfo is None:
            raise NftInvariantError("marketplace listing history date must be timezone-aware")

        object.__setattr__(self, "status", normalized_status)
        object.__setattr__(self, "reason", normalized_reason)


@dataclass(frozen=True)
class MarketplaceListing:
    id: UUID
    seller_id: UUID
    card_id: UUID
    token_id: int
    price: int
    status: MarketplaceListingStatus
    expires_at: datetime
    created_at: datetime
    history: tuple[MarketplaceListingHistoryEntry, ...]

    def __post_init__(self) -> None:
        normalized_status = MarketplaceListingStatus(self.status)

        if self.token_id <= 0:
            raise NftInvariantError("marketplace listing token id must be positive")

        if self.price <= 0:
            raise NftInvariantError("marketplace listing price must be positive")

        if self.created_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise NftInvariantError("marketplace listing dates must be timezone-aware")

        if self.expires_at <= self.created_at:
            raise NftInvariantError("marketplace listing expiration must be after creation")

        if not self.history:
            raise NftInvariantError("marketplace listing history cannot be empty")

        if self.history[-1].status != normalized_status:
            raise NftInvariantError("marketplace listing status must match latest history entry")

        object.__setattr__(self, "status", normalized_status)

    def is_expired(self, checked_at: datetime | None = None) -> bool:
        if self.status != MarketplaceListingStatus.ACTIVE:
            return False

        return self.expires_at <= (checked_at or datetime.now(UTC))

    def expire(self, checked_at: datetime | None = None) -> "MarketplaceListing":
        resolved_checked_at = checked_at or datetime.now(UTC)

        if not self.is_expired(resolved_checked_at):
            return self

        return self._with_status(
            MarketplaceListingStatus.EXPIRED,
            changed_at=resolved_checked_at,
            reason="listing expired",
        )

    def cancel(
        self,
        *,
        cancelled_at: datetime | None = None,
        reason: str = "seller cancelled listing",
    ) -> "MarketplaceListing":
        return self._active_transition(
            MarketplaceListingStatus.CANCELLED,
            changed_at=cancelled_at or datetime.now(UTC),
            reason=reason,
        )

    def mark_sold(
        self,
        *,
        sold_at: datetime | None = None,
        reason: str = "marketplace sale completed",
    ) -> "MarketplaceListing":
        return self._active_transition(
            MarketplaceListingStatus.SOLD,
            changed_at=sold_at or datetime.now(UTC),
            reason=reason,
        )

    def _active_transition(
        self,
        status: MarketplaceListingStatus,
        *,
        changed_at: datetime,
        reason: str,
    ) -> "MarketplaceListing":
        if self.is_expired(changed_at):
            raise NftInvariantError("expired marketplace listing cannot change status")

        if self.status != MarketplaceListingStatus.ACTIVE:
            raise NftInvariantError("marketplace listing status can change only from active")

        return self._with_status(status, changed_at=changed_at, reason=reason)

    def _with_status(
        self,
        status: MarketplaceListingStatus,
        *,
        changed_at: datetime,
        reason: str,
    ) -> "MarketplaceListing":
        history_entry = MarketplaceListingHistoryEntry(
            status=status,
            changed_at=changed_at,
            reason=reason,
        )

        return MarketplaceListing(
            id=self.id,
            seller_id=self.seller_id,
            card_id=self.card_id,
            token_id=self.token_id,
            price=self.price,
            status=status,
            expires_at=self.expires_at,
            created_at=self.created_at,
            history=(*self.history, history_entry),
        )


def create_nft_metadata(
    *,
    card_id: UUID,
    card_name: str,
    family: str,
    rarity: int,
    level: int,
    speed: int | None = None,
    strength: int | None = None,
    intelligence: int | None = None,
    resistance: int | None = None,
    expires_at: datetime | None = None,
    generated_at: datetime | None = None,
) -> NftMetadata:
    attributes = [
        NftAttribute("Family", family),
        NftAttribute("Rarity", rarity),
        NftAttribute("Level", level),
    ]
    optional_attributes = {
        "Speed": speed,
        "Strength": strength,
        "Intelligence": intelligence,
        "Resistance": resistance,
        "Expires At": expires_at.isoformat() if expires_at else None,
    }

    for trait_type, value in optional_attributes.items():
        if value is not None:
            attributes.append(NftAttribute(trait_type, value))

    return NftMetadata(
        card_id=card_id,
        name=f"Super Trunfo NFT - {card_name}",
        description=(
            f"Offline ERC-721 metadata for {card_name}, a Super Trunfo card "
            f"from the {family} family prepared for post-MVP mint."
        ),
        image=f"{NFT_IMAGE_BASE_URI}/{card_id}.png",
        attributes=tuple(attributes),
        generated_at=generated_at or datetime.now(UTC),
        mint_enabled=False,
    )


def create_marketplace_listing(
    *,
    seller_id: UUID,
    card_id: UUID,
    token_id: int,
    price: int,
    expires_at: datetime,
    listing_id: UUID | None = None,
    created_at: datetime | None = None,
) -> MarketplaceListing:
    resolved_created_at = created_at or datetime.now(UTC)

    return MarketplaceListing(
        id=listing_id or uuid4(),
        seller_id=seller_id,
        card_id=card_id,
        token_id=token_id,
        price=price,
        status=MarketplaceListingStatus.ACTIVE,
        expires_at=expires_at,
        created_at=resolved_created_at,
        history=(
            MarketplaceListingHistoryEntry(
                status=MarketplaceListingStatus.ACTIVE,
                changed_at=resolved_created_at,
                reason="listing created",
            ),
        ),
    )
