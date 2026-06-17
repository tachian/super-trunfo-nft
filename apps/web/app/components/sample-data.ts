export type CardRarity = "common" | "rare" | "epic" | "legendary";

export type CollectionCard = {
  id: string;
  name: string;
  family: string;
  rarity: CardRarity;
  level: number;
  expiresAt: string;
  speed: number;
  strength: number;
  intelligence: number;
  resistance: number;
};

export type ShopOffer = {
  id: string;
  title: string;
  price: number;
  rarity: CardRarity;
  expiresIn: string;
};

export type RankingEntry = {
  position: number;
  nickname: string;
  tier: string;
  rating: number;
  wins: number;
};

export const collectionCards: CollectionCard[] = [
  {
    id: "card-aurora-01",
    name: "Aurora Runner",
    family: "Solar",
    rarity: "rare",
    level: 84,
    expiresAt: "2026-09-08T18:00:00Z",
    speed: 91,
    strength: 64,
    intelligence: 77,
    resistance: 70,
  },
  {
    id: "card-granite-02",
    name: "Granite Guard",
    family: "Terra",
    rarity: "epic",
    level: 88,
    expiresAt: "2026-09-11T18:00:00Z",
    speed: 59,
    strength: 93,
    intelligence: 68,
    resistance: 96,
  },
  {
    id: "card-pulse-03",
    name: "Pulse Scholar",
    family: "Arcano",
    rarity: "legendary",
    level: 95,
    expiresAt: "2026-10-01T18:00:00Z",
    speed: 76,
    strength: 71,
    intelligence: 98,
    resistance: 82,
  },
  {
    id: "card-river-04",
    name: "River Sentinel",
    family: "Agua",
    rarity: "common",
    level: 71,
    expiresAt: "2026-08-29T18:00:00Z",
    speed: 74,
    strength: 69,
    intelligence: 66,
    resistance: 75,
  },
  {
    id: "card-ember-05",
    name: "Ember Striker",
    family: "Fogo",
    rarity: "rare",
    level: 82,
    expiresAt: "2026-09-15T18:00:00Z",
    speed: 86,
    strength: 84,
    intelligence: 67,
    resistance: 72,
  },
  {
    id: "card-mist-06",
    name: "Mist Oracle",
    family: "Agua",
    rarity: "epic",
    level: 90,
    expiresAt: "2026-11-02T18:00:00Z",
    speed: 72,
    strength: 61,
    intelligence: 96,
    resistance: 83,
  },
  {
    id: "card-iron-07",
    name: "Iron Howl",
    family: "Terra",
    rarity: "common",
    level: 68,
    expiresAt: "2026-08-18T18:00:00Z",
    speed: 63,
    strength: 78,
    intelligence: 58,
    resistance: 81,
  },
  {
    id: "card-neon-08",
    name: "Neon Tactician",
    family: "Arcano",
    rarity: "rare",
    level: 86,
    expiresAt: "2026-12-09T18:00:00Z",
    speed: 80,
    strength: 70,
    intelligence: 91,
    resistance: 76,
  },
  {
    id: "card-gale-09",
    name: "Gale Scout",
    family: "Vento",
    rarity: "common",
    level: 73,
    expiresAt: "2026-09-24T18:00:00Z",
    speed: 88,
    strength: 60,
    intelligence: 69,
    resistance: 67,
  },
  {
    id: "card-crystal-10",
    name: "Crystal Warden",
    family: "Solar",
    rarity: "epic",
    level: 89,
    expiresAt: "2026-10-20T18:00:00Z",
    speed: 70,
    strength: 86,
    intelligence: 82,
    resistance: 92,
  },
  {
    id: "card-tide-11",
    name: "Tide Duelist",
    family: "Agua",
    rarity: "rare",
    level: 80,
    expiresAt: "2026-07-31T18:00:00Z",
    speed: 84,
    strength: 73,
    intelligence: 78,
    resistance: 74,
  },
  {
    id: "card-ash-12",
    name: "Ash Keeper",
    family: "Fogo",
    rarity: "common",
    level: 65,
    expiresAt: "2026-05-01T18:00:00Z",
    speed: 61,
    strength: 69,
    intelligence: 64,
    resistance: 71,
  },
];

export const initialDeckCardIds = collectionCards
  .filter((card) => card.id !== "card-ash-12")
  .slice(0, 10)
  .map((card) => card.id);

export const deckCards = collectionCards.filter((card) =>
  initialDeckCardIds.includes(card.id),
);

export const shopOffers: ShopOffer[] = [
  {
    id: "offer-rare-pack",
    title: "Pack raro",
    price: 45,
    rarity: "rare",
    expiresIn: "12h",
  },
  {
    id: "offer-renewal",
    title: "Renovacao epica",
    price: 30,
    rarity: "epic",
    expiresIn: "1d",
  },
  {
    id: "offer-starter",
    title: "Reforco inicial",
    price: 18,
    rarity: "common",
    expiresIn: "3d",
  },
];

export const rankingEntries: RankingEntry[] = [
  {
    position: 1,
    nickname: "TachiMaster",
    tier: "Diamond",
    rating: 1842,
    wins: 42,
  },
  {
    position: 2,
    nickname: "DeckForge",
    tier: "Platinum",
    rating: 1710,
    wins: 36,
  },
  {
    position: 3,
    nickname: "CardPilot",
    tier: "Gold",
    rating: 1596,
    wins: 29,
  },
  {
    position: 4,
    nickname: "ByteTrunfo",
    tier: "Gold",
    rating: 1532,
    wins: 24,
  },
];

export function rarityLabel(rarity: CardRarity): string {
  const labels: Record<CardRarity, string> = {
    common: "Comum",
    rare: "Raro",
    epic: "Epico",
    legendary: "Lendario",
  };

  return labels[rarity];
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeZone: "UTC",
  }).format(new Date(value));
}
