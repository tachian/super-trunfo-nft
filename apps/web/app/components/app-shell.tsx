"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BadgeCent,
  Layers3,
  Library,
  LogIn,
  LogOut,
  Play,
  Store,
  Trophy,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
};

const NAV_ITEMS: NavItem[] = [
  { href: "/login", label: "Login", icon: LogIn },
  { href: "/colecao", label: "Colecao", icon: Library },
  { href: "/deck", label: "Deck", icon: Layers3 },
  { href: "/partida", label: "Partida", icon: Play },
  { href: "/loja", label: "Loja", icon: Store },
  { href: "/ranking", label: "Ranking", icon: Trophy },
];

export function AppShell({
  children,
  eyebrow,
  title,
  toolbar,
}: {
  children: ReactNode;
  eyebrow: string;
  title: string;
  toolbar?: ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  function handleLogout() {
    window.sessionStorage.removeItem("super-trunfo.auth.token");
    router.push("/login");
  }

  return (
    <main className="app-frame">
      <aside className="sidebar" aria-label="Navegacao principal">
        <Link className="brand" href="/colecao" aria-label="Super Trunfo NFT">
          <Image
            src="/card-back.svg"
            width={48}
            height={67}
            alt=""
            aria-hidden="true"
            priority
          />
          <span>Super Trunfo NFT</span>
        </Link>

        <nav className="main-nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link
                aria-current={isActive ? "page" : undefined}
                className={isActive ? "active" : undefined}
                href={item.href}
                key={item.href}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-status" aria-label="Resumo do jogador">
          <BadgeCent size={18} aria-hidden="true" />
          <div>
            <span>Saldo</span>
            <strong>128 creditos</strong>
          </div>
        </div>
        <button className="logout-action" type="button" onClick={handleLogout}>
          <LogOut size={18} aria-hidden="true" />
          Sair
        </button>
      </aside>

      <section className="workspace">
        <header className="page-heading">
          <div>
            <p className="eyebrow">{eyebrow}</p>
            <h1>{title}</h1>
          </div>
          {toolbar ? <div className="toolbar">{toolbar}</div> : null}
        </header>
        {children}
      </section>
    </main>
  );
}
