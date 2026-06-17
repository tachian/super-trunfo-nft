import { Crown, Trophy } from "lucide-react";
import { AppShell } from "../components/app-shell";
import type { RankingEntry } from "../components/sample-data";
import { rankingEntries } from "../components/sample-data";

export default function RankingPage() {
  return (
    <AppShell
      eyebrow="Temporada atual"
      title="Ranking"
      toolbar={
        <button className="secondary-action" type="button">
          <Trophy size={18} aria-hidden="true" />
          Global
        </button>
      }
    >
      <section className="leaderboard" aria-label="Ranking global">
        {rankingEntries.map(renderRankingEntry)}
      </section>
    </AppShell>
  );
}

function renderRankingEntry(entry: RankingEntry) {
  return (
    <article className="leader-row" key={entry.nickname}>
      <span className="leader-position">
        {entry.position === 1 ? (
          <Crown size={18} aria-hidden="true" />
        ) : (
          entry.position
        )}
      </span>
      <div>
        <strong>{entry.nickname}</strong>
        <span>{entry.tier}</span>
      </div>
      <dl>
        <div>
          <dt>Rating</dt>
          <dd>{entry.rating}</dd>
        </div>
        <div>
          <dt>Vitorias</dt>
          <dd>{entry.wins}</dd>
        </div>
      </dl>
    </article>
  );
}
