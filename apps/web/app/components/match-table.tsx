"use client";

import Image from "next/image";
import { RotateCcw, Send, Swords } from "lucide-react";
import { useMemo, useState } from "react";
import { attributeLabel, deckCards, rarityLabel } from "./sample-data";
import type { CardAttributeKey, CollectionCard } from "./sample-data";

type RoundWinner = "player" | "opponent" | "draw";

type RoundResult = {
  round: number;
  attribute: CardAttributeKey;
  playerCard: string;
  opponentCard: string;
  playerValue: number;
  opponentValue: number;
  winner: RoundWinner;
};

const attributes: CardAttributeKey[] = [
  "speed",
  "strength",
  "intelligence",
  "resistance",
];

const opponentCardNames = [
  "Circuit Ranger",
  "Basalt Keeper",
  "Vector Sage",
  "Wave Anchor",
  "Flame Runner",
  "Cloud Adept",
  "Steel Roamer",
  "Neon Baron",
  "Gale Binder",
  "Crystal Guard",
];

const botOffsets = [
  { speed: -4, strength: 8, intelligence: -2, resistance: 3 },
  { speed: 9, strength: -6, intelligence: 7, resistance: -4 },
  { speed: -2, strength: 4, intelligence: -5, resistance: 6 },
  { speed: 5, strength: -3, intelligence: 4, resistance: -2 },
];

const opponentDeck = deckCards.map((card, index) => ({
  ...card,
  id: `bot-${card.id}`,
  name: opponentCardNames[index] ?? `BOT Card ${index + 1}`,
  speed: Math.max(50, card.speed + botOffsets[index % botOffsets.length].speed),
  strength: Math.max(
    50,
    card.strength + botOffsets[index % botOffsets.length].strength,
  ),
  intelligence: Math.max(
    50,
    card.intelligence + botOffsets[index % botOffsets.length].intelligence,
  ),
  resistance: Math.max(
    50,
    card.resistance + botOffsets[index % botOffsets.length].resistance,
  ),
}));

const totalRounds = Math.min(deckCards.length, opponentDeck.length);

export function MatchTable() {
  const [selectedAttribute, setSelectedAttribute] =
    useState<CardAttributeKey>("intelligence");
  const [roundIndex, setRoundIndex] = useState(0);
  const [roundResults, setRoundResults] = useState<RoundResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const activeRoundIndex = Math.min(roundIndex, totalRounds - 1);
  const playerCard = deckCards[activeRoundIndex];
  const opponentCard = opponentDeck[activeRoundIndex];
  const matchIsFinished = roundResults.length === totalRounds;

  const score = useMemo(() => {
    return roundResults.reduce(
      (currentScore, result) => {
        if (result.winner === "player") {
          return { ...currentScore, player: currentScore.player + 1 };
        }

        if (result.winner === "opponent") {
          return { ...currentScore, opponent: currentScore.opponent + 1 };
        }

        return currentScore;
      },
      { player: 0, opponent: 0 },
    );
  }, [roundResults]);

  const resultLabel = matchResultLabel(score, matchIsFinished);

  function handlePlayRound() {
    if (matchIsFinished) {
      setError("Partida encerrada.");
      return;
    }

    const playerValue = playerCard[selectedAttribute];
    const opponentValue = opponentCard[selectedAttribute];
    const winner = roundWinner(playerValue, opponentValue);
    const nextResult: RoundResult = {
      round: roundIndex + 1,
      attribute: selectedAttribute,
      playerCard: playerCard.name,
      opponentCard: opponentCard.name,
      playerValue,
      opponentValue,
      winner,
    };

    setRoundResults([...roundResults, nextResult]);
    setRoundIndex(Math.min(roundIndex + 1, totalRounds - 1));
    setError(null);
  }

  function handleRestart() {
    setRoundIndex(0);
    setRoundResults([]);
    setSelectedAttribute("intelligence");
    setError(null);
  }

  return (
    <section className="match-table" aria-label="Mesa de partida">
      <section className="match-status-grid" aria-label="Estado da partida">
        <article className="stat-tile">
          <span>Rodada</span>
          <strong>
            {Math.min(roundResults.length + 1, totalRounds)}/{totalRounds}
          </strong>
        </article>
        <article className="stat-tile">
          <span>Placar</span>
          <strong>
            {score.player} x {score.opponent}
          </strong>
        </article>
        <article className="stat-tile">
          <span>Resultado</span>
          <strong>{resultLabel}</strong>
        </article>
      </section>

      <section className="match-arena" aria-label="Cartas da rodada">
        <BattleCard
          card={playerCard}
          label="Jogador"
          selectedAttribute={selectedAttribute}
        />
        <div className="versus-panel" aria-label="Atributo selecionado">
          <Swords size={30} aria-hidden="true" />
          <span>Atributo selecionado</span>
          <strong>{attributeLabel(selectedAttribute)}</strong>
          <small>
            {matchIsFinished ? "Partida encerrada" : `Rodada ${roundIndex + 1}`}
          </small>
        </div>
        <BattleCard
          card={opponentCard}
          label="BOT"
          selectedAttribute={selectedAttribute}
        />
      </section>

      <section className="attribute-panel" aria-label="Atributos">
        {attributes.map((attribute) => (
          <button
            className={
              selectedAttribute === attribute
                ? "attribute-button selected"
                : "attribute-button"
            }
            disabled={matchIsFinished}
            key={attribute}
            type="button"
            onClick={() => setSelectedAttribute(attribute)}
          >
            <span>{attributeLabel(attribute)}</span>
            <strong>{playerCard[attribute]}</strong>
          </button>
        ))}
      </section>

      {error ? (
        <p className="validation warning" role="alert">
          {error}
        </p>
      ) : null}

      <section className="match-actions" aria-label="Acoes da partida">
        <button
          className="primary-action"
          disabled={matchIsFinished}
          type="button"
          onClick={handlePlayRound}
        >
          <Send size={18} aria-hidden="true" />
          Enviar jogada
        </button>
        <button
          className="secondary-action"
          type="button"
          onClick={handleRestart}
        >
          <RotateCcw size={18} aria-hidden="true" />
          Reiniciar
        </button>
      </section>

      <section className="round-history" aria-label="Historico de rodadas">
        <div className="section-heading">
          <p className="eyebrow">Rodadas</p>
          <h2>Replay</h2>
        </div>
        <div className="round-list">
          {roundResults.map((result) => (
            <article className="round-row" key={result.round}>
              <span>#{result.round}</span>
              <strong>{attributeLabel(result.attribute)}</strong>
              <small>
                {result.playerValue} x {result.opponentValue}
              </small>
              <em>{roundWinnerLabel(result.winner)}</em>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}

function BattleCard({
  card,
  label,
  selectedAttribute,
}: {
  card: CollectionCard;
  label: string;
  selectedAttribute: CardAttributeKey;
}) {
  return (
    <article className="battle-card detailed">
      <Image
        src="/card-back.svg"
        width={110}
        height={153}
        alt=""
        aria-hidden="true"
      />
      <div>
        <p className="eyebrow">{label}</p>
        <h2>{card.name}</h2>
        <span>{rarityLabel(card.rarity)}</span>
        <dl className="battle-attributes">
          {attributes.map((attribute) => (
            <div
              className={
                selectedAttribute === attribute ? "active-attribute" : undefined
              }
              key={attribute}
            >
              <dt>{attributeLabel(attribute)}</dt>
              <dd>{card[attribute]}</dd>
            </div>
          ))}
        </dl>
      </div>
    </article>
  );
}

function roundWinner(playerValue: number, opponentValue: number): RoundWinner {
  if (playerValue > opponentValue) {
    return "player";
  }

  if (opponentValue > playerValue) {
    return "opponent";
  }

  return "draw";
}

function roundWinnerLabel(winner: RoundWinner): string {
  const labels: Record<RoundWinner, string> = {
    player: "Jogador",
    opponent: "BOT",
    draw: "Empate",
  };

  return labels[winner];
}

function matchResultLabel(
  score: { player: number; opponent: number },
  matchIsFinished: boolean,
): string {
  if (!matchIsFinished) {
    return "Em andamento";
  }

  if (score.player > score.opponent) {
    return "Vitoria";
  }

  if (score.opponent > score.player) {
    return "Derrota";
  }

  return "Empate";
}
