import { existsSync } from "node:fs";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const requiredFiles = [
  "openapi/platform.yaml",
  "events/domain-events.yaml",
  "domain/domain-contracts.yaml",
];
const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..");

for (const file of requiredFiles) {
  if (!existsSync(join(packageRoot, file))) {
    throw new Error(`Missing contract file: ${file}`);
  }
}

const platformContract = readFileSync(
  join(packageRoot, "openapi/platform.yaml"),
  "utf8",
);
const requiredAuthContractFragments = [
  "operationId: registerPlayer",
  "operationId: loginPlayer",
  '$ref: "#/components/schemas/RegisterPlayerRequest"',
  '$ref: "#/components/schemas/LoginPlayerRequest"',
  '$ref: "#/components/schemas/AuthResponse"',
  "operationId: getCurrentPlayerProfile",
  '$ref: "#/components/schemas/PlayerProfile"',
  '$ref: "#/components/schemas/OnboardingRewards"',
  '$ref: "#/components/schemas/InitialDeckCard"',
  "initial_deck_tenth_card_credit",
  "bearerAuth:",
];

for (const fragment of requiredAuthContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing auth contract fragment: ${fragment}`);
  }
}

console.log("API contracts present.");
