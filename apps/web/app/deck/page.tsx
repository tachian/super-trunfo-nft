import Image from "next/image";
import { Layers3 } from "lucide-react";
import { AppShell } from "../components/app-shell";
import { deckCards, rarityLabel } from "../components/sample-data";

const deckAverage = Math.round(
  deckCards.reduce((total, card) => total + card.level, 0) / deckCards.length,
);

export default function DeckPage() {
  return (
    <AppShell
      eyebrow="Deck ativo"
      title="Selecao de deck"
      toolbar={
        <button className="primary-action" type="button">
          <Layers3 size={18} aria-hidden="true" />
          Salvar deck
        </button>
      }
    >
      <section className="stat-grid" aria-label="Resumo do deck">
        <article className="stat-tile">
          <span>Selecionadas</span>
          <strong>{deckCards.length}/10</strong>
        </article>
        <article className="stat-tile">
          <span>Nivel medio</span>
          <strong>{deckAverage}</strong>
        </article>
        <article className="stat-tile">
          <span>Tolerancia</span>
          <strong>+/-20</strong>
        </article>
      </section>

      <section className="deck-builder" aria-label="Cartas selecionadas">
        {deckCards.map((card) => (
          <article className="deck-slot" key={card.id}>
            <Image
              src="/card-back.svg"
              width={64}
              height={89}
              alt=""
              aria-hidden="true"
            />
            <div>
              <strong>{card.name}</strong>
              <span>
                {rarityLabel(card.rarity)} · Nivel {card.level}
              </span>
            </div>
            <dl className="compact-attributes">
              <div>
                <dt>Vel</dt>
                <dd>{card.speed}</dd>
              </div>
              <div>
                <dt>For</dt>
                <dd>{card.strength}</dd>
              </div>
              <div>
                <dt>Int</dt>
                <dd>{card.intelligence}</dd>
              </div>
              <div>
                <dt>Res</dt>
                <dd>{card.resistance}</dd>
              </div>
            </dl>
          </article>
        ))}
      </section>
    </AppShell>
  );
}
