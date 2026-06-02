from threading import Lock
from uuid import UUID

from app.domain.entities import Card
from app.domain.exceptions import DuplicateCardHashError
from app.domain.repositories import CardSearchDocument


class InMemoryCardRepository:
    def __init__(self) -> None:
        self._cards_by_hash: dict[str, Card] = {}
        self._cards_by_id: dict[UUID, Card] = {}
        self._lock = Lock()

    def add(self, card: Card) -> None:
        with self._lock:
            if card.uniqueness_hash in self._cards_by_hash:
                raise DuplicateCardHashError("identical card already exists")

            self._cards_by_hash[card.uniqueness_hash] = card
            self._cards_by_id[card.id] = card

    def exists_by_uniqueness_hash(self, uniqueness_hash: str) -> bool:
        return uniqueness_hash in self._cards_by_hash

    def find_by_id(self, card_id: UUID) -> Card | None:
        return self._cards_by_id.get(card_id)

    def clear(self) -> None:
        with self._lock:
            self._cards_by_hash.clear()
            self._cards_by_id.clear()


class InMemoryCardSearchIndex:
    def __init__(self) -> None:
        self._documents_by_id: dict[UUID, CardSearchDocument] = {}
        self._lock = Lock()

    def index(self, card: Card, generation_batch_id: UUID) -> None:
        document = CardSearchDocument(
            card_id=card.id,
            owner_id=card.owner_id,
            name=card.name,
            family=card.family,
            rarity=card.rarity,
            level=card.level,
            expires_at=card.expires_at,
            uniqueness_hash=card.uniqueness_hash,
            generation_batch_id=generation_batch_id,
        )

        with self._lock:
            self._documents_by_id[card.id] = document

    def find_by_owner(self, owner_id: UUID) -> tuple[CardSearchDocument, ...]:
        return tuple(
            document
            for document in self._documents_by_id.values()
            if document.owner_id == owner_id
        )

    def clear(self) -> None:
        with self._lock:
            self._documents_by_id.clear()
