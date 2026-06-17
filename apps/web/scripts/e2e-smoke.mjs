import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const sourceChecks = [
  {
    file: "app/login/page.tsx",
    fragments: ["/auth/login", "window.sessionStorage.setItem"],
  },
  {
    file: "app/components/collection-deck-manager.tsx",
    fragments: [
      "selectedCardIds.length >= 10",
      "Salvar deck",
      "Carta expirada nao pode entrar no deck.",
    ],
  },
  {
    file: "app/partida/page.tsx",
    fragments: ["Buscar partida", "<MatchTable />"],
  },
  {
    file: "app/components/match-table.tsx",
    fragments: ["Enviar jogada", "roundResults", "Resultado"],
  },
  {
    file: "app/loja/page.tsx",
    fragments: ["Comprar", "shopOffers"],
  },
];

for (const check of sourceChecks) {
  const path = join(appRoot, check.file);
  assert(existsSync(path), `Missing E2E route source: ${check.file}`);

  const source = readFileSync(path, "utf8");

  for (const fragment of check.fragments) {
    assert(
      source.includes(fragment),
      `Missing E2E source fragment "${fragment}" in ${check.file}`,
    );
  }
}

const services = createMockServices();
const session = await services.auth.login({
  credentialSecret: smokeCredentialSecret(),
  email: "player@example.test",
});
assert(session.accessToken.startsWith("mock-token-"), "Login token not issued");

const collection = await services.cards.list(session.accessToken);
const selectedCardIds = collection
  .filter((card) => !card.expired)
  .slice(0, 10)
  .map((card) => card.id);

const deck = await services.cards.selectDeck(session.accessToken, {
  cardIds: selectedCardIds,
});
assert(deck.cardIds.length === 10, "Deck selection must contain 10 cards");
assert(deck.averageLevel > 0, "Deck average level must be calculated");

const ticket = await services.matchmaking.find(session.accessToken, {
  deckId: deck.id,
  averageLevel: deck.averageLevel,
});
assert(ticket.status === "matched_with_bot", "Matchmaking fallback failed");

let match = await services.gameplay.get(ticket.matchId);
assert(match.status === "in_progress", "Match was not created");

for (const attribute of ["intelligence", "speed", "strength", "resistance"]) {
  match = await services.gameplay.play(session.accessToken, {
    attribute,
    matchId: match.id,
  });

  if (match.status === "completed") {
    break;
  }
}

assert(match.rounds.length > 0, "Match must record at least one round");
assert(match.score.player + match.score.opponent > 0, "Score was not updated");

const offers = await services.economy.offers(session.accessToken);
assert(offers.length > 0, "Shop offers must be available");

const purchase = await services.economy.buy(session.accessToken, {
  offerId: offers[0].id,
});
assert(purchase.walletBalance < 128, "Wallet balance was not debited");
assert(purchase.inventoryCardId, "Purchased card was not added to inventory");

console.log("Web E2E smoke passed.");

function createMockServices() {
  const player = {
    id: "player-smoke-001",
    credits: 128,
    token: "mock-token-player-smoke-001",
  };
  const cards = buildSmokeCards();
  const matches = new Map();
  const offers = [
    {
      id: "offer-rare-pack",
      inventoryCardId: "card-purchased-rare",
      price: 45,
    },
  ];

  return {
    auth: {
      async login(payload) {
        assert(payload.email.includes("@"), "Login email must be valid");
        assert(
          payload.credentialSecret.length >= 8,
          "Login credential must be valid",
        );

        return {
          accessToken: player.token,
          playerId: player.id,
        };
      },
    },
    cards: {
      async list(token) {
        assertToken(token, player.token);
        return cards;
      },
      async selectDeck(token, payload) {
        assertToken(token, player.token);
        assert(payload.cardIds.length === 10, "Deck requires 10 cards");

        const selectedCards = payload.cardIds.map((cardId) => {
          const card = cards.find((item) => item.id === cardId);
          assert(card, `Card not found: ${cardId}`);
          assert(!card.expired, `Expired card selected: ${cardId}`);
          return card;
        });

        return {
          averageLevel: averageLevel(selectedCards),
          cardIds: payload.cardIds,
          id: "deck-smoke-001",
        };
      },
    },
    matchmaking: {
      async find(token, payload) {
        assertToken(token, player.token);
        assert(payload.averageLevel > 0, "Average level is required");

        const match = createMatch(payload.deckId);
        matches.set(match.id, match);

        return {
          matchId: match.id,
          status: "matched_with_bot",
        };
      },
    },
    gameplay: {
      async get(matchId) {
        const match = matches.get(matchId);
        assert(match, `Match not found: ${matchId}`);
        return match;
      },
      async play(token, payload) {
        assertToken(token, player.token);
        const match = matches.get(payload.matchId);
        assert(match, `Match not found: ${payload.matchId}`);
        assert(match.status !== "completed", "Match already completed");

        const nextRound = match.rounds.length + 1;
        const playerCard = cards[nextRound - 1];
        const botCard = cards[nextRound + 1];
        const playerValue = playerCard[payload.attribute];
        const botValue = Math.max(50, botCard[payload.attribute] - 3);

        if (playerValue >= botValue) {
          match.score.player += 1;
        } else {
          match.score.opponent += 1;
        }

        match.rounds.push({
          attribute: payload.attribute,
          botValue,
          playerValue,
          round: nextRound,
        });

        if (match.rounds.length >= 4) {
          match.status = "completed";
          match.result =
            match.score.player >= match.score.opponent ? "player" : "bot";
        }

        return match;
      },
    },
    economy: {
      async offers(token) {
        assertToken(token, player.token);
        return offers;
      },
      async buy(token, payload) {
        assertToken(token, player.token);
        const offer = offers.find((item) => item.id === payload.offerId);
        assert(offer, `Offer not found: ${payload.offerId}`);
        assert(player.credits >= offer.price, "Insufficient credits");

        player.credits -= offer.price;

        return {
          inventoryCardId: offer.inventoryCardId,
          walletBalance: player.credits,
        };
      },
    },
  };
}

function buildSmokeCards() {
  return [
    smokeCard("card-01", 91, 64, 77, 70),
    smokeCard("card-02", 59, 93, 68, 96),
    smokeCard("card-03", 76, 71, 98, 82),
    smokeCard("card-04", 74, 69, 66, 75),
    smokeCard("card-05", 86, 84, 67, 72),
    smokeCard("card-06", 72, 61, 96, 83),
    smokeCard("card-07", 63, 78, 58, 81),
    smokeCard("card-08", 80, 70, 91, 76),
    smokeCard("card-09", 88, 60, 69, 67),
    smokeCard("card-10", 70, 86, 82, 92),
    { ...smokeCard("card-expired", 60, 60, 60, 60), expired: true },
  ];
}

function smokeCard(id, speed, strength, intelligence, resistance) {
  return {
    expired: false,
    id,
    intelligence,
    level: speed + strength + intelligence + resistance,
    resistance,
    speed,
    strength,
  };
}

function createMatch(deckId) {
  return {
    deckId,
    id: "match-smoke-001",
    result: null,
    rounds: [],
    score: { opponent: 0, player: 0 },
    status: "in_progress",
  };
}

function averageLevel(cards) {
  const total = cards.reduce((sum, card) => sum + card.level, 0);
  return Math.round(total / cards.length);
}

function assertToken(receivedToken, expectedToken) {
  assert(receivedToken === expectedToken, "Invalid session token");
}

function smokeCredentialSecret() {
  return (
    process.env.SUPER_TRUNFO_E2E_SECRET ??
    `smoke-${process.platform}-${process.version}`
  );
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}
