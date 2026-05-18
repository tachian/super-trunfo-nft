import Image from "next/image";
import { BadgeCent, Swords, Trophy, UsersRound } from "lucide-react";

const cards = [
  { name: "Shadow Titan", family: "Titans", level: 393, rarity: "Epico" },
  { name: "Solar Lynx", family: "Solar", level: 344, rarity: "Raro" },
  { name: "Iron Oracle", family: "Oracle", level: 318, rarity: "Comum" },
];

const metrics = [
  { label: "Rating", value: "1480", icon: Trophy },
  { label: "Creditos", value: "12", icon: BadgeCent },
  { label: "Deck", value: "9/10", icon: Swords },
  { label: "Amigos", value: "24", icon: UsersRound },
];

export default function Home() {
  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Navegacao principal">
        <Image
          src="/card-back.svg"
          width={72}
          height={100}
          alt="Carta Super Trunfo"
          priority
        />
        <nav>
          <a href="#deck">Deck</a>
          <a href="#matchmaking">Matchmaking</a>
          <a href="#ranking">Ranking</a>
          <a href="#shop">Loja</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">MVP competitivo</p>
            <h1>Super Trunfo NFT</h1>
          </div>
          <button type="button" className="primary-action">
            <Swords size={18} aria-hidden="true" />
            Buscar partida
          </button>
        </header>

        <section className="metrics" aria-label="Indicadores do jogador">
          {metrics.map((metric) => {
            const Icon = metric.icon;
            return (
              <article key={metric.label} className="metric">
                <Icon size={20} aria-hidden="true" />
                <span>{metric.label}</span>
                <strong>{metric.value}</strong>
              </article>
            );
          })}
        </section>

        <section className="board">
          <div className="match-panel" id="matchmaking">
            <p className="eyebrow">Fila bronze</p>
            <h2>Matchmaking por nivel medio do deck</h2>
            <div className="queue-meter" aria-label="Tolerancia de pareamento">
              <span style={{ width: "68%" }} />
            </div>
            <p>
              Busca ativa em faixa de +/-20 pontos. Fallback PvE preparado para
              BOT equivalente.
            </p>
          </div>

          <div className="deck-panel" id="deck">
            <div className="section-heading">
              <p className="eyebrow">Colecao</p>
              <h2>Deck inicial</h2>
            </div>
            <div className="cards-grid">
              {cards.map((card) => (
                <article key={card.name} className="card-tile">
                  <Image
                    src="/card-back.svg"
                    width={54}
                    height={76}
                    alt=""
                    aria-hidden="true"
                  />
                  <div>
                    <strong>{card.name}</strong>
                    <span>{card.family}</span>
                    <small>
                      {card.rarity} · Nivel {card.level}
                    </small>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
