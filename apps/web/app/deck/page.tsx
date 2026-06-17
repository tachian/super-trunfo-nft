import { AppShell } from "../components/app-shell";
import { CollectionDeckManager } from "../components/collection-deck-manager";

export default function DeckPage() {
  return (
    <AppShell eyebrow="Deck ativo" title="Selecao de deck">
      <CollectionDeckManager />
    </AppShell>
  );
}
