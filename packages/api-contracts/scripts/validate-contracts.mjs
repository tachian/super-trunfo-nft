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

const requiredCardContractFragments = [
  "Card:",
  "CardAttributes:",
  "Deck:",
  "SelectDeckRequest:",
  "operationId: selectDeck",
  "owner_id:",
  "expires_at:",
  "average_level:",
  "Derived from speed + strength + intelligence + resistance + rarity.",
];

for (const fragment of requiredCardContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing card contract fragment: ${fragment}`);
  }
}

const requiredNftContractFragments = [
  "operationId: generateOfflineNftMetadata",
  "operationId: getNftMetadata",
  "GenerateNftMetadataRequest:",
  "NftMetadata:",
  "NftAttribute:",
  "mint_enabled:",
  "enum: [false]",
];

for (const fragment of requiredNftContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing NFT contract fragment: ${fragment}`);
  }
}

const requiredGameplayContractFragments = [
  "operationId: getMatchState",
  "operationId: playRound",
  "operationId: getMatchReplay",
  "GameplayMatch:",
  "GameplayParticipant:",
  "GameplayRound:",
  "GameplayScore:",
  "PlayRoundRequest:",
  "MatchReplay:",
  "additionalProperties: false",
  "enum: [in_progress, finished, abandoned]",
  "enum: [speed, strength, intelligence, resistance, rarity]",
];

for (const fragment of requiredGameplayContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing gameplay contract fragment: ${fragment}`);
  }
}

const requiredMatchmakingContractFragments = [
  "operationId: findMatch",
  "operationId: getMatchmakingQueues",
  "FindMatchRequest:",
  "FindMatchResponse:",
  "MatchmakingTicket:",
  "enum: [queued, matched]",
  "enum: [20]",
  "MatchmakingQueue:",
  "MatchmakingQueues:",
  "enum: [queue:bronze, queue:silver, queue:gold]",
  "enum: [ST-401]",
  "enum: [redis]",
];

for (const fragment of requiredMatchmakingContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing matchmaking contract fragment: ${fragment}`);
  }
}

const domainContracts = readFileSync(
  join(packageRoot, "domain/domain-contracts.yaml"),
  "utf8",
);
const requiredGameplayDomainFragments = [
  "BotStrategy",
  "BOT deck must be equivalent",
  "BOT strategy prefers the strongest card attribute",
];

for (const fragment of requiredGameplayDomainFragments) {
  if (!domainContracts.includes(fragment)) {
    throw new Error(`Missing gameplay domain contract fragment: ${fragment}`);
  }
}

const requiredMatchmakingDomainFragments = [
  "Matchmaking Redis queues are named queue:bronze, queue:silver and queue:gold.",
  "Players are paired only when their average deck levels differ by at most 20 points.",
];

for (const fragment of requiredMatchmakingDomainFragments) {
  if (!domainContracts.includes(fragment)) {
    throw new Error(
      `Missing matchmaking domain contract fragment: ${fragment}`,
    );
  }
}

const domainEventsContract = readFileSync(
  join(packageRoot, "events/domain-events.yaml"),
  "utf8",
);
const requiredIdentityEventFragments = [
  "name: PlayerRegistered",
  "name: PlayerLoggedIn",
  "version: 1.0.0",
  "initial_deck_size: integer",
  "initial_credits: integer",
  "player_id: uuid",
];

for (const fragment of requiredIdentityEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing identity event contract fragment: ${fragment}`);
  }
}

const requiredNftEventFragments = [
  "name: NftMetadataGenerated",
  "producer: nft-service",
  "metadata_uri: string",
  "mint_enabled: boolean",
];

for (const fragment of requiredNftEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing NFT event contract fragment: ${fragment}`);
  }
}

const requiredCardEventFragments = [
  "name: DeckSelected",
  "producer: card-service",
  "card_ids: uuid[]",
  "average_level: number",
];

for (const fragment of requiredCardEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing card event contract fragment: ${fragment}`);
  }
}

console.log("API contracts present.");
