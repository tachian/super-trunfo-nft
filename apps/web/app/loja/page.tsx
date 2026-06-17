import { ShoppingCart, Store } from "lucide-react";
import { AppShell } from "../components/app-shell";
import { rarityLabel, shopOffers } from "../components/sample-data";

export default function ShopPage() {
  return (
    <AppShell
      eyebrow="Economia"
      title="Loja"
      toolbar={
        <button className="secondary-action" type="button">
          <Store size={18} aria-hidden="true" />
          Ofertas
        </button>
      }
    >
      <section className="stat-grid" aria-label="Resumo da loja">
        <article className="stat-tile">
          <span>Saldo</span>
          <strong>128</strong>
        </article>
        <article className="stat-tile">
          <span>Ofertas</span>
          <strong>{shopOffers.length}</strong>
        </article>
        <article className="stat-tile">
          <span>Inventario</span>
          <strong>4</strong>
        </article>
      </section>

      <section className="offer-grid" aria-label="Ofertas ativas">
        {shopOffers.map((offer) => (
          <article className="offer-tile" key={offer.id}>
            <div>
              <span>{rarityLabel(offer.rarity)}</span>
              <strong>{offer.title}</strong>
            </div>
            <dl>
              <div>
                <dt>Preco</dt>
                <dd>{offer.price}</dd>
              </div>
              <div>
                <dt>Expira</dt>
                <dd>{offer.expiresIn}</dd>
              </div>
            </dl>
            <button className="primary-action" type="button">
              <ShoppingCart size={18} aria-hidden="true" />
              Comprar
            </button>
          </article>
        ))}
      </section>
    </AppShell>
  );
}
