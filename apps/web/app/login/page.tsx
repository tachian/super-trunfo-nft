"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  CircleAlert,
  LogIn,
  ShieldCheck,
  Trophy,
  UserPlus,
} from "lucide-react";

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

type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  player: PlayerSummary;
};

type AuthPayload = {
  nickname?: string;
  email: string;
  password: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [authMode, setAuthMode] = useState<AuthMode>("login");
  const [requestState, setRequestState] = useState<RequestState>("idle");
  const [player, setPlayer] = useState<PlayerSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = window.sessionStorage.getItem(SESSION_TOKEN_KEY);

    if (storedToken) {
      setRequestState("authenticated");
    }
  }, []);

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
      setPlayer(authResponse.player);
      setRequestState("authenticated");
      router.push("/colecao");
    } catch (caughtError) {
      setRequestState("idle");
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Nao foi possivel autenticar.",
      );
    }
  }

  return (
    <main className="login-page">
      <section className="login-visual" aria-label="Super Trunfo NFT">
        <div className="card-stack" aria-hidden="true">
          <span className="mini-card rare" />
          <span className="mini-card epic" />
          <span className="mini-card legendary" />
        </div>
        <div>
          <p className="eyebrow">Acesso MVP</p>
          <h1>Super Trunfo NFT</h1>
        </div>
        <dl className="login-stats">
          <div>
            <dt>Rating base</dt>
            <dd>1000</dd>
          </div>
          <div>
            <dt>Deck inicial</dt>
            <dd>10 cartas</dd>
          </div>
          <div>
            <dt>Creditos</dt>
            <dd>100</dd>
          </div>
        </dl>
      </section>

      <section className="login-panel" aria-label="Sessao do jogador">
        <form className="auth-form" onSubmit={handleAuthSubmit}>
          <div className="section-heading">
            <p className="eyebrow">Sessao do jogador</p>
            <h2>{authMode === "login" ? "Entrar" : "Criar conta"}</h2>
          </div>

          <div className="mode-switch" role="tablist" aria-label="Modo">
            <button
              type="button"
              aria-selected={authMode === "login"}
              className={authMode === "login" ? "selected" : ""}
              onClick={() => setAuthMode("login")}
            >
              <LogIn size={17} aria-hidden="true" />
              Entrar
            </button>
            <button
              type="button"
              aria-selected={authMode === "register"}
              className={authMode === "register" ? "selected" : ""}
              onClick={() => setAuthMode("register")}
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
            disabled={requestState === "loading"}
          >
            {authMode === "login" ? (
              <LogIn size={18} aria-hidden="true" />
            ) : (
              <UserPlus size={18} aria-hidden="true" />
            )}
            {requestState === "loading"
              ? "Processando"
              : authMode === "login"
                ? "Entrar"
                : "Criar conta"}
          </button>
        </form>

        <div className="session-state">
          {requestState === "authenticated" ? (
            <>
              <Trophy size={20} aria-hidden="true" />
              <span>{player?.nickname ?? "Sessao ativa"}</span>
            </>
          ) : (
            <>
              <ShieldCheck size={20} aria-hidden="true" />
              <span>Aguardando credenciais</span>
            </>
          )}
        </div>
      </section>
    </main>
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
