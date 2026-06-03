from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urlparse
from uuid import UUID

from .exceptions import NftInvariantError

NftAttributeValue = int | str
NFT_IMAGE_BASE_URI = "ipfs://super-trunfo-nft/cards"


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
