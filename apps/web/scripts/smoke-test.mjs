import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const requiredFiles = [
  "app/page.tsx",
  "app/layout.tsx",
  "app/components/app-shell.tsx",
  "app/components/collection-deck-manager.tsx",
  "app/components/sample-data.ts",
  "app/login/page.tsx",
  "app/colecao/page.tsx",
  "app/deck/page.tsx",
  "app/partida/page.tsx",
  "app/loja/page.tsx",
  "app/ranking/page.tsx",
  "public/card-back.svg",
];
const appRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

for (const file of requiredFiles) {
  if (!existsSync(join(appRoot, file))) {
    throw new Error(`Missing web app file: ${file}`);
  }
}

const pageSource = readFileSync(join(appRoot, "app/page.tsx"), "utf8");
const shellSource = readFileSync(
  join(appRoot, "app/components/app-shell.tsx"),
  "utf8",
);
const collectionDeckSource = readFileSync(
  join(appRoot, "app/components/collection-deck-manager.tsx"),
  "utf8",
);
const loginSource = readFileSync(join(appRoot, "app/login/page.tsx"), "utf8");
const requiredFragments = [
  'redirect("/login")',
  "Super Trunfo NFT",
  "/colecao",
  "/deck",
  "/partida",
  "/loja",
  "/ranking",
  "rarityFilter",
  "familyFilter",
  "selectedCardIds.length >= 10",
  "Carta expirada nao pode entrar no deck.",
  "SESSION_TOKEN_KEY",
  "/auth/login",
  "/auth/register",
  "window.sessionStorage.removeItem",
  "window.sessionStorage.setItem",
];

for (const fragment of requiredFragments) {
  if (
    !pageSource.includes(fragment) &&
    !shellSource.includes(fragment) &&
    !collectionDeckSource.includes(fragment) &&
    !loginSource.includes(fragment)
  ) {
    throw new Error(`Missing web shell fragment: ${fragment}`);
  }
}

console.log("Web smoke test passed.");
