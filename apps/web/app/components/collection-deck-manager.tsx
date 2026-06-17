"use client";

import Image from "next/image";
import { Save, Search } from "lucide-react";
import { useMemo, useState } from "react";
import {
  collectionCards,
  formatDate,
  initialDeckCardIds,
  rarityLabel,
} from "./sample-data";
import type { CardRarity, CollectionCard } from "./sample-data";

type CardFilter = CardRarity | "all";

export function CollectionDeckManager() {
  const [rarityFilter, setRarityFilter] = useState<CardFilter>("all");
  const [familyFilter, setFamilyFilter] = useState("all");
  const [selectedCardIds, setSelectedCardIds] =
    useState<string[]>(initialDeckCardIds);
  const [validationMessage, setValidationMessage] = useState(
    "Deck valido para matchmaking.",
  );

  const families = useMemo(() => {
    return [...new Set(collectionCards.map((card) => card.family))].sort();
  }, []);

  const filteredCards = useMemo(() => {
    return collectionCards.filter((card) => {
      const matchesRarity =
        rarityFilter === "all" || card.rarity === rarityFilter;
      const matchesFamily =
        familyFilter === "all" || card.family === familyFilter;

      return matchesRarity && matchesFamily;
    });
  }, [familyFilter, rarityFilter]);

  const selectedCards = useMemo(() => {
    return selectedCardIds
      .map((cardId) => collectionCards.find((card) => card.id === cardId))
      .filter((card): card is CollectionCard => card !== undefined);
  }, [selectedCardIds]);

  const deckAverage = useMemo(() => {
    if (selectedCards.length === 0) {
      return 0;
    }

    const levelTotal = selectedCards.reduce(
      (total, card) => total + card.level,
      0,
    );

    return Math.round(levelTotal / selectedCards.length);
  }, [selectedCards]);

  const deckIsComplete = selectedCards.length === 10;

  function handleSelection(card: CollectionCard) {
    if (cardIsExpired(card)) {
      setValidationMessage("Carta expirada nao pode entrar no deck.");
      return;
    }

    if (selectedCardIds.includes(card.id)) {
      const nextSelection = selectedCardIds.filter(
        (cardId) => cardId !== card.id,
      );
      setSelectedCardIds(nextSelection);
      setValidationMessage("Deck precisa ter exatamente 10 cartas.");
      return;
    }

    if (selectedCardIds.length >= 10) {
      setValidationMessage("Remova uma carta antes de adicionar outra.");
      return;
    }

    const nextSelection = [...selectedCardIds, card.id];
    setSelectedCardIds(nextSelection);
    setValidationMessage(
      nextSelection.length === 10
        ? "Deck valido para matchmaking."
        : "Deck precisa ter exatamente 10 cartas.",
    );
  }

  return (
    <section className="collection-workspace" aria-label="Colecao e deck">
      <section className="stat-grid" aria-label="Resumo do deck">
        <article className="stat-tile">
          <span>Selecionadas</span>
          <strong>{selectedCards.length}/10</strong>
        </article>
        <article className="stat-tile">
          <span>Nivel medio</span>
          <strong>{deckAverage}</strong>
        </article>
        <article className="stat-tile">
          <span>Status</span>
          <strong>{deckIsComplete ? "Valido" : "Pendente"}</strong>
        </article>
      </section>

      <section className="collection-filters" aria-label="Filtros da colecao">
        <label>
          <Search size={18} aria-hidden="true" />
          Raridade
          <select
            value={rarityFilter}
            onChange={(event) =>
              setRarityFilter(event.currentTarget.value as CardFilter)
            }
          >
            <option value="all">Todas</option>
            <option value="common">Comum</option>
            <option value="rare">Raro</option>
            <option value="epic">Epico</option>
            <option value="legendary">Lendario</option>
          </select>
        </label>
        <label>
          Familia
          <select
            value={familyFilter}
            onChange={(event) => setFamilyFilter(event.currentTarget.value)}
          >
            <option value="all">Todas</option>
            {families.map((family) => (
              <option key={family} value={family}>
                {family}
              </option>
            ))}
          </select>
        </label>
      </section>

      <div className="collection-layout">
        <section className="cards-grid collection-grid" aria-label="Cartas">
          {filteredCards.map((card) => {
            const isSelected = selectedCardIds.includes(card.id);
            const isExpired = cardIsExpired(card);

            return (
              <article
                className={
                  isSelected ? "card-tile full selected" : "card-tile full"
                }
                key={card.id}
              >
                <Image
                  src="/card-back.svg"
                  width={72}
                  height={100}
                  alt=""
                  aria-hidden="true"
                />
                <div className="card-body">
                  <div>
                    <strong>{card.name}</strong>
                    <span>{card.family}</span>
                  </div>
                  <dl className="card-attributes">
                    <div>
                      <dt>Nivel</dt>
                      <dd>{card.level}</dd>
                    </div>
                    <div>
                      <dt>Raridade</dt>
                      <dd>{rarityLabel(card.rarity)}</dd>
                    </div>
                    <div>
                      <dt>Validade</dt>
                      <dd>
                        {isExpired ? "Expirada" : formatDate(card.expiresAt)}
                      </dd>
                    </div>
                  </dl>
                  <label className="selection-control">
                    <input
                      checked={isSelected}
                      disabled={isExpired}
                      type="checkbox"
                      onChange={() => handleSelection(card)}
                    />
                    {isSelected ? "No deck" : "Selecionar"}
                  </label>
                </div>
              </article>
            );
          })}
        </section>

        <aside className="deck-review" aria-label="Deck selecionado">
          <div className="section-heading">
            <p className="eyebrow">Deck selecionado</p>
            <h2>{selectedCards.length}/10 cartas</h2>
          </div>
          <p
            className={
              deckIsComplete ? "validation success" : "validation warning"
            }
            role="status"
          >
            {validationMessage}
          </p>
          <div className="deck-list">
            {selectedCards.map((card) => (
              <button
                className="deck-list-item"
                key={card.id}
                type="button"
                onClick={() => handleSelection(card)}
              >
                <span>{card.name}</span>
                <strong>Nivel {card.level}</strong>
              </button>
            ))}
          </div>
          <button
            className="primary-action"
            disabled={!deckIsComplete}
            type="button"
          >
            <Save size={18} aria-hidden="true" />
            Salvar deck
          </button>
        </aside>
      </div>
    </section>
  );
}

function cardIsExpired(card: CollectionCard): boolean {
  return new Date(card.expiresAt).getTime() < Date.now();
}
