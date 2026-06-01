"use client";

import Image from "next/image";
import {
  BadgeCent,
  CircleAlert,
  LogIn,
  LogOut,
  ShieldCheck,
  Swords,
  Trophy,
  UserPlus,
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8001";
const SESSION_TOKEN_KEY = "super-trunfo.auth.token";

type AuthMode = "login" | "register";
type RequestState = "idle" | "loading" | "authenticated";

const AUTH_ENDPOINTS: Record<AuthMode, string> = {
  login: "/auth/login",
  register: "/auth/register",
};

type PlayerSummary = {
  id: string;
  nickname: string;
  rating: number;
  credits: number;
};

type SocialLoginMetadata = {
  provider: string;
  subject: string | null;
};

type InitialDeckCard = {
  id: string;
  name: string;
  level: number;
  expires_at: string;
  family: string;
  rarity_label: string;
  speed: number;
  strength: number;
  intelligence: number;
  resistance: number;
  rarity: number;
};

type OnboardingRewards = {
  initial_deck: InitialDeckCard[];
  initial_credits: number;
  credit_ledger: Array<{
    id: string;
    amount: number;
    reason: string;
    created_at: string;
  }>;
  granted_at: string;
};

type PlayerProfile = PlayerSummary & {
  created_at: string;
  social_login: SocialLoginMetadata;
  onboarding: OnboardingRewards;
};

type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  player: PlayerSummary;
  onboarding: OnboardingRewards;
};

type AuthPayload = {
  nickname?: string;
  email: string;
  password: string;
};

export default function Home() {
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [profile, setProfile] = useState<PlayerProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const isAuthenticated = profile !== null;

  useEffect(() => {
    const storedToken = window.sessionStorage.getItem(SESSION_TOKEN_KEY);

    if (!storedToken) {
      return;
    }

    setRequestState("loading");
    fetchCurrentProfile(storedToken)
      .then((loadedProfile) => {
        setProfile(loadedProfile);
        setRequestState("authenticated");
      })
      .catch(() => {
        window.sessionStorage.removeItem(SESSION_TOKEN_KEY);
        setRequestState("idle");
      });
  }, []);

  const deckAverageLevel = useMemo(() => {
    if (!profile) {
      return 0;
    }

    const total = profile.onboarding.initial_deck.reduce(
      (sum, card) => sum + card.level,
      0,
    );

    return Math.round(total / profile.onboarding.initial_deck.length);
  }, [profile]);

  async function handleAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setRequestState("loading");

    const form = new FormData(event.currentTarget);
    const payload: AuthPayload = {
      email: String(form.get("email") ?? ""),
      password: String(form.get("password") ?? ""),
    };

    if (authMode === "register") {
      payload.nickname = String(form.get("nickname") ?? "");
    }

    try {
      const authResponse = await authenticate(authMode, payload);
      window.sessionStorage.setItem(
        SESSION_TOKEN_KEY,
        authResponse.access_token,
      );
      const loadedProfile = await fetchCurrentProfile(
        authResponse.access_token,
      );

      setProfile(loadedProfile);
      setRequestState("authenticated");
    } catch (caughtError) {
      setRequestState("idle");
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Nao foi possivel autenticar.",
      );
    }
  }

  function handleLogout() {
    window.sessionStorage.removeItem(SESSION_TOKEN_KEY);
    setProfile(null);
    setError(null);
    setRequestState("idle");
  }

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Navegacao principal">
        <Image
          src="/card-back.svg"
          width={72}
          height={100}
          alt="Carta Super Trunfo"
          priority
        />
        <nav>
          <a href="#sessao">Sessao</a>
          <a href="#perfil">Perfil</a>
          <a href="#deck">Deck</a>
          <a href="#matchmaking">Matchmaking</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Identity MVP</p>
            <h1>Super Trunfo NFT</h1>
          </div>
          {isAuthenticated ? (
            <button
              type="button"
              className="secondary-action"
              onClick={handleLogout}
            >
              <LogOut size={18} aria-hidden="true" />
              Sair
            </button>
          ) : null}
        </header>

        {isAuthenticated ? (
          <AuthenticatedDashboard
            deckAverageLevel={deckAverageLevel}
            onLogout={handleLogout}
            profile={profile}
          />
        ) : (
          <AuthPanel
            authMode={authMode}
            error={error}
            isSubmitting={requestState === "loading"}
            onModeChange={setAuthMode}
            onSubmit={handleAuthSubmit}
          />
        )}
      </section>
    </main>
  );
}

function AuthPanel({
  authMode,
  error,
  isSubmitting,
  onModeChange,
  onSubmit,
}: {
  authMode: AuthMode;
  error: string | null;
  isSubmitting: boolean;
  onModeChange: (mode: AuthMode) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <section className="auth-layout" id="sessao">
      <form className="auth-panel" onSubmit={onSubmit}>
        <div className="section-heading">
          <p className="eyebrow">Sessao do jogador</p>
          <h2>{authMode === "login" ? "Entrar" : "Criar conta"}</h2>
        </div>

        <div className="mode-switch" role="tablist" aria-label="Modo de acesso">
          <button
            type="button"
            aria-selected={authMode === "login"}
            className={authMode === "login" ? "selected" : ""}
            onClick={() => onModeChange("login")}
          >
            <LogIn size={17} aria-hidden="true" />
            Entrar
          </button>
          <button
            type="button"
            aria-selected={authMode === "register"}
            className={authMode === "register" ? "selected" : ""}
            onClick={() => onModeChange("register")}
          >
            <UserPlus size={17} aria-hidden="true" />
            Criar
          </button>
        </div>

        {authMode === "register" ? (
          <label>
            Nickname
            <input
              name="nickname"
              autoComplete="nickname"
              minLength={3}
              maxLength={50}
              required
            />
          </label>
        ) : null}

        <label>
          Email
          <input name="email" type="email" autoComplete="email" required />
        </label>

        <label>
          Senha
          <input
            name="password"
            type="password"
            autoComplete={
              authMode === "login" ? "current-password" : "new-password"
            }
            minLength={8}
            maxLength={128}
            required
          />
        </label>

        {error ? (
          <p className="form-error" role="alert">
            <CircleAlert size={16} aria-hidden="true" />
            {error}
          </p>
        ) : null}

        <button
          type="submit"
          className="primary-action"
          disabled={isSubmitting}
        >
          {authMode === "login" ? (
            <LogIn size={18} aria-hidden="true" />
          ) : (
            <UserPlus size={18} aria-hidden="true" />
          )}
          {isSubmitting
            ? "Processando"
            : authMode === "login"
              ? "Entrar"
              : "Criar conta"}
        </button>
      </form>

      <section className="session-panel" aria-label="Estado da sessao">
        <ShieldCheck size={28} aria-hidden="true" />
        <div>
          <p className="eyebrow">Estado autenticado</p>
          <h2>Aguardando jogador</h2>
        </div>
      </section>
    </section>
  );
}

function AuthenticatedDashboard({
  deckAverageLevel,
  onLogout,
  profile,
}: {
  deckAverageLevel: number;
  onLogout: () => void;
  profile: PlayerProfile;
}) {
  const metrics = [
    { label: "Rating", value: String(profile.rating), icon: Trophy },
    { label: "Creditos", value: String(profile.credits), icon: BadgeCent },
    {
      label: "Deck",
      value: `${profile.onboarding.initial_deck.length}/10`,
      icon: Swords,
    },
    {
      label: "Nivel medio",
      value: String(deckAverageLevel),
      icon: ShieldCheck,
    },
  ];

  return (
    <>
      <section className="metrics" aria-label="Indicadores do jogador">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article key={metric.label} className="metric">
              <Icon size={20} aria-hidden="true" />
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </article>
          );
        })}
      </section>

      <section className="profile-band" id="perfil">
        <div>
          <p className="eyebrow">Perfil autenticado</p>
          <h2>{profile.nickname}</h2>
        </div>
        <dl>
          <div>
            <dt>Provider</dt>
            <dd>{profile.social_login.provider}</dd>
          </div>
          <div>
            <dt>Criado em</dt>
            <dd>{formatDate(profile.created_at)}</dd>
          </div>
          <div>
            <dt>Jogador</dt>
            <dd>{profile.id.slice(0, 8)}</dd>
          </div>
        </dl>
        <button type="button" className="secondary-action" onClick={onLogout}>
          <LogOut size={18} aria-hidden="true" />
          Encerrar sessao
        </button>
      </section>

      <section className="board">
        <section className="match-panel" id="matchmaking">
          <p className="eyebrow">Fila bronze</p>
          <h2>Matchmaking por nivel medio</h2>
          <div className="queue-meter" aria-label="Tolerancia de pareamento">
            <span
              style={{ width: `${Math.min(deckAverageLevel / 4, 100)}%` }}
            />
          </div>
          <dl className="match-stats">
            <div>
              <dt>Base</dt>
              <dd>{deckAverageLevel}</dd>
            </div>
            <div>
              <dt>Min</dt>
              <dd>{deckAverageLevel - 20}</dd>
            </div>
            <div>
              <dt>Max</dt>
              <dd>{deckAverageLevel + 20}</dd>
            </div>
          </dl>
        </section>

        <section className="deck-panel" id="deck">
          <div className="section-heading">
            <p className="eyebrow">Colecao inicial</p>
            <h2>Deck concedido</h2>
          </div>
          <div className="cards-grid">
            {profile.onboarding.initial_deck.map((card) => (
              <article key={card.id} className="card-tile">
                <Image
                  src="/card-back.svg"
                  width={54}
                  height={76}
                  alt=""
                  aria-hidden="true"
                />
                <div>
                  <strong>{card.name}</strong>
                  <span>{card.family}</span>
                  <small>
                    {rarityLabel(card.rarity_label)} · Nivel {card.level}
                  </small>
                </div>
              </article>
            ))}
          </div>
        </section>
      </section>
    </>
  );
}

async function authenticate(
  mode: AuthMode,
  payload: AuthPayload,
): Promise<AuthResponse> {
  return requestJson<AuthResponse>(AUTH_ENDPOINTS[mode], {
    body: JSON.stringify(payload),
    headers: { "Content-Type": "application/json" },
    method: "POST",
  });
}

async function fetchCurrentProfile(token: string): Promise<PlayerProfile> {
  return requestJson<PlayerProfile>("/players/me", {
    headers: { Authorization: `Bearer ${token}` },
    method: "GET",
  });
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String(body.detail)
        : "Requisicao recusada pelo servico.";

    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function rarityLabel(value: string): string {
  const labels: Record<string, string> = {
    common: "Comum",
    rare: "Raro",
    epic: "Epico",
  };

  return labels[value] ?? value;
}
