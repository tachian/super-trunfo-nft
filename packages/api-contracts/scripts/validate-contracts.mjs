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
  "operationId: createMarketplaceListing",
  "operationId: listMarketplaceListings",
  "GenerateNftMetadataRequest:",
  "NftMetadata:",
  "NftAttribute:",
  "NftMintFeatureFlagResponse:",
  "CreateMarketplaceListingRequest:",
  "MarketplaceListing:",
  "MarketplaceListingHistoryEntry:",
  "mint_enabled:",
  "feature_nft_enabled:",
  "enum: [ST-705]",
  "enum: [disabled, enabled]",
  "enum: [active, expired, cancelled, sold]",
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
  "operationId: streamMatchEvents",
  "x-websocket: true",
  "GameplayMatch:",
  "GameplayParticipant:",
  "GameplayRound:",
  "GameplayScore:",
  "GameplayRealtimeEvent:",
  "PlayRoundRequest:",
  "MatchReplay:",
  "AttributeSelected",
  "RoundFinished",
  "MatchResultUpdated",
  "PlayerRankUpdated",
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
  "MatchmakingOpponent:",
  "MatchmakingMatch:",
  "MatchmakingEvent:",
  "fallback_after_seconds:",
  "enum: [queued, matched, pve_created]",
  "enum: [pvp, pve]",
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

const requiredEconomyContractFragments = [
  "operationId: getWalletCredits",
  "operationId: applyMatchResultCredits",
  "operationId: listShopOffers",
  "operationId: buyShopOffer",
  "operationId: getEconomicTelemetry",
  "EconomyWalletCredits:",
  "EconomyCreditLedgerEntry:",
  "ApplyMatchResultCreditsRequest:",
  "ApplyMatchResultCreditsResponse:",
  "ShopOfferResponse:",
  "ShopOffersResponse:",
  "BuyShopOfferRequest:",
  "BuyShopOfferResponse:",
  "EconomicTelemetryResponse:",
  "EconomicCreditTelemetryResponse:",
  "EconomicBalanceTelemetryResponse:",
  "EconomicRiskTelemetryResponse:",
  "EconomyPurchase:",
  "EconomyInventoryCard:",
  "EconomyEvent:",
  "enum: [victory, defeat]",
  "enum: [match_victory, match_defeat]",
  "enum: [ST-501]",
  "enum: [ST-502]",
  "enum: [ST-505]",
  "enum: [stable, watch, critical]",
  "enum: [economy-service]",
];

for (const fragment of requiredEconomyContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing economy contract fragment: ${fragment}`);
  }
}

const requiredRankingContractFragments = [
  "operationId: getGlobalRanking",
  "operationId: getFriendsRanking",
  "operationId: recalculatePlayerRating",
  "RankingLeaderboardResponse:",
  "LeaderboardEntryResponse:",
  "RankingCache:",
  "RecalculatePlayerRatingRequest:",
  "RecalculatePlayerRatingResponse:",
  "RankingRating:",
  "RankingEvent:",
  "enum: [bronze, silver, gold, platinum, diamond]",
  "enum: [ST-503]",
  "enum: [ST-504]",
  "enum: [global, friends]",
  "enum: [ranking-service]",
  "additionalProperties: false",
];

for (const fragment of requiredRankingContractFragments) {
  if (!platformContract.includes(fragment)) {
    throw new Error(`Missing ranking contract fragment: ${fragment}`);
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
  "Gameplay publishes realtime WebSocket events for attribute selection, round result, match result and ranking updates.",
];

for (const fragment of requiredGameplayDomainFragments) {
  if (!domainContracts.includes(fragment)) {
    throw new Error(`Missing gameplay domain contract fragment: ${fragment}`);
  }
}

const requiredMatchmakingDomainFragments = [
  "Matchmaking Redis queues are named queue:bronze, queue:silver and queue:gold.",
  "Players are paired only when their average deck levels differ by at most 20 points.",
  "PvE fallback creates a BOT opponent with the same average deck level as the player ticket.",
  "Matchmaking publishes MatchStarted when a PvP or PvE match is created.",
];

for (const fragment of requiredMatchmakingDomainFragments) {
  if (!domainContracts.includes(fragment)) {
    throw new Error(
      `Missing matchmaking domain contract fragment: ${fragment}`,
    );
  }
}

const requiredEconomyDomainFragments = [
  "Match victory grants one credit in the MVP.",
  "Defeat grants zero credits in the MVP.",
  "Credit ledger prevents duplicate grants per player and match.",
  "CreditsEarned is published only when a new positive credit entry is created.",
  "Purchases must be atomic against wallet balance and inventory.",
  "Shop offers must have a positive price and explicit expiration.",
  "BuyShopOffer rejects expired offers and insufficient wallet credits.",
  "Economic telemetry exposes aggregated metrics only, without player identifiers.",
  "Win streak abuse signal starts at five consecutive victories.",
  "Inflation status is derived from credit spend ratio and average wallet balance.",
];

for (const fragment of requiredEconomyDomainFragments) {
  if (!domainContracts.includes(fragment)) {
    throw new Error(`Missing economy domain contract fragment: ${fragment}`);
  }
}

const requiredRankingDomainFragments = [
  "Default rating starts at 1000 points.",
  "RecalculatePlayerRating uses simplified ELO with K-factor 32.",
  "Rating recalculation is idempotent per match.",
  "Global leaderboard is ordered by score, wins, losses and player id.",
  "Leaderboard queries use cache keys scoped by repository version and pagination.",
  "Friends leaderboard returns an empty cached list when no friend ids are provided.",
  "Bronze tier ranges from 0 to 999.",
  "Diamond tier starts at 2500.",
];

for (const fragment of requiredRankingDomainFragments) {
  if (!domainContracts.includes(fragment)) {
    throw new Error(`Missing ranking domain contract fragment: ${fragment}`);
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
  "name: MarketplaceListingCreated",
  "name: TradeCreated",
  "name: TradeAccepted",
  "name: TradeCancelled",
  "name: NFTTransferred",
  "producer: nft-service",
  "metadata_uri: string",
  "mint_enabled: boolean",
  "listing_id: uuid",
  "trade_id: uuid",
  "seller_id: uuid",
  "buyer_id: uuid",
  "token_id: integer",
  "from_player_id: uuid",
  "to_player_id: uuid",
  "transferred_at: datetime",
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

const requiredGameplayEventFragments = [
  "name: AttributeSelected",
  "name: RoundFinished",
  "name: MatchResultUpdated",
  "producer: gameplay-service",
  "selected_attribute: string",
  "player_score: integer",
  "opponent_score: integer",
];

for (const fragment of requiredGameplayEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing gameplay event contract fragment: ${fragment}`);
  }
}

const requiredMatchmakingEventFragments = [
  "name: MatchStarted",
  "producer: matchmaking-service",
  "mode: string",
  "opponent_kind: string",
  "player_average_deck_level: integer",
  "opponent_average_deck_level: integer",
  "name: BotMatchCreated",
  "bot_average_deck_level: integer",
];

for (const fragment of requiredMatchmakingEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing matchmaking event contract fragment: ${fragment}`);
  }
}

const requiredEconomyEventFragments = [
  "name: CreditsEarned",
  "name: OfferPurchased",
  "producer: economy-service",
  "ledger_entry_id: uuid",
  "purchase_id: uuid",
  "inventory_card_id: uuid",
  "offer_id: uuid",
  "purchased_at: datetime",
  "amount: integer",
  "balance: integer",
  "earned_at: datetime",
];

for (const fragment of requiredEconomyEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing economy event contract fragment: ${fragment}`);
  }
}

const requiredRankingEventFragments = [
  "name: PlayerRankUpdated",
  "producer: ranking-service",
  "previous_score: integer",
  "score: integer",
  "delta: integer",
  "tier: string",
  "matches_played: integer",
  "updated_at: datetime",
];

for (const fragment of requiredRankingEventFragments) {
  if (!domainEventsContract.includes(fragment)) {
    throw new Error(`Missing ranking event contract fragment: ${fragment}`);
  }
}

console.log("API contracts present.");
