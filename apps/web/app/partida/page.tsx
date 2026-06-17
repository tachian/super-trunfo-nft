import { Play } from "lucide-react";
import { AppShell } from "../components/app-shell";
import { MatchTable } from "../components/match-table";

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
      <MatchTable />
    </AppShell>
  );
}
