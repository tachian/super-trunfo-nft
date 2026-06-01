import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const requiredFiles = [
  "app/page.tsx",
  "app/layout.tsx",
  "public/card-back.svg",
];
const appRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

for (const file of requiredFiles) {
  if (!existsSync(join(appRoot, file))) {
    throw new Error(`Missing web app file: ${file}`);
  }
}

const pageSource = readFileSync(join(appRoot, "app/page.tsx"), "utf8");
const requiredFragments = [
  "SESSION_TOKEN_KEY",
  "/auth/login",
  "/auth/register",
  "/players/me",
  "window.sessionStorage.removeItem",
  "onboarding.initial_deck",
];

for (const fragment of requiredFragments) {
  if (!pageSource.includes(fragment)) {
    throw new Error(`Missing web auth flow fragment: ${fragment}`);
  }
}

console.log("Web smoke test passed.");
