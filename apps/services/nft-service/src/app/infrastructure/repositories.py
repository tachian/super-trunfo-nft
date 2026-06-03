from threading import Lock
from uuid import UUID

from app.domain.entities import NftMetadata


class InMemoryNftMetadataRepository:
    def __init__(self) -> None:
        self._metadata_by_card_id: dict[UUID, NftMetadata] = {}
        self._lock = Lock()

    def save(self, metadata: NftMetadata) -> None:
        with self._lock:
            self._metadata_by_card_id[metadata.card_id] = metadata

    def find_by_card_id(self, card_id: UUID) -> NftMetadata | None:
        return self._metadata_by_card_id.get(card_id)

    def clear(self) -> None:
        with self._lock:
            self._metadata_by_card_id.clear()
