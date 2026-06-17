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
];

export const deckCards = collectionCards.slice(0, 3);

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
