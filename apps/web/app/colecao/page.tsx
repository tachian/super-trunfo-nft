import { AppShell } from "../components/app-shell";
import { CollectionDeckManager } from "../components/collection-deck-manager";

export default function CollectionPage() {
  return (
    <AppShell eyebrow="Cards" title="Colecao">
      <CollectionDeckManager />
    </AppShell>
  );
}
