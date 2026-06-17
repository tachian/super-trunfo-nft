import Image from "next/image";
import { Search } from "lucide-react";
import { AppShell } from "../components/app-shell";
import {
  collectionCards,
  formatDate,
  rarityLabel,
} from "../components/sample-data";

export default function CollectionPage() {
  return (
    <AppShell
      eyebrow="Cards"
      title="Colecao"
      toolbar={
        <button className="secondary-action" type="button">
          <Search size={18} aria-hidden="true" />
          Filtrar
        </button>
      }
    >
      <section className="stat-grid" aria-label="Resumo da colecao">
        <article className="stat-tile">
          <span>Total</span>
          <strong>{collectionCards.length}</strong>
        </article>
        <article className="stat-tile">
          <span>Familias</span>
          <strong>4</strong>
        </article>
        <article className="stat-tile">
          <span>Raridade maior</span>
          <strong>Lendario</strong>
        </article>
      </section>

      <section className="cards-grid collection-grid" aria-label="Cartas">
        {collectionCards.map((card) => (
          <article className="card-tile full" key={card.id}>
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
                  <dd>{formatDate(card.expiresAt)}</dd>
                </div>
              </dl>
            </div>
          </article>
        ))}
      </section>
    </AppShell>
  );
}
