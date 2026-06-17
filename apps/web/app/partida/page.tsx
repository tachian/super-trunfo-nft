import Image from "next/image";
import { Play, Swords } from "lucide-react";
import { AppShell } from "../components/app-shell";
import { deckCards } from "../components/sample-data";

const activeCard = deckCards[0];

export default function MatchPage() {
  return (
    <AppShell
      eyebrow="Mesa MVP"
      title="Partida"
      toolbar={
        <button className="primary-action" type="button">
          <Play size={18} aria-hidden="true" />
          Buscar partida
        </button>
      }
    >
      <section className="match-board" aria-label="Partida atual">
        <article className="battle-card">
          <Image
            src="/card-back.svg"
            width={120}
            height={167}
            alt=""
            aria-hidden="true"
            priority
          />
          <div>
            <p className="eyebrow">Sua carta</p>
            <h2>{activeCard.name}</h2>
            <dl className="battle-attributes">
              <div>
                <dt>Velocidade</dt>
                <dd>{activeCard.speed}</dd>
              </div>
              <div>
                <dt>Forca</dt>
                <dd>{activeCard.strength}</dd>
              </div>
              <div>
                <dt>Inteligencia</dt>
                <dd>{activeCard.intelligence}</dd>
              </div>
              <div>
                <dt>Resistencia</dt>
                <dd>{activeCard.resistance}</dd>
              </div>
            </dl>
          </div>
        </article>

        <section className="round-panel" aria-label="Rodada">
          <Swords size={28} aria-hidden="true" />
          <div>
            <p className="eyebrow">Rodada 1 de 10</p>
            <h2>Atributo selecionado: Inteligencia</h2>
          </div>
          <dl className="score-line">
            <div>
              <dt>Jogador</dt>
              <dd>0</dd>
            </div>
            <div>
              <dt>Oponente</dt>
              <dd>0</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>Fila</dd>
            </div>
          </dl>
        </section>
      </section>
    </AppShell>
  );
}
