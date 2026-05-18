# Mapa DDD e Arquitetura Hexagonal

Fonte principal: `docs/Arquitetura Jogo Super Trunfo Nft Ddd.pdf`.

## Objetivo

Definir os limites de dominio da plataforma Super Trunfo NFT e registrar como cada contexto conversa com os demais sem acoplamento direto de banco, framework ou UI.

## Padrao Arquitetural

Cada servico deve seguir arquitetura hexagonal:

- `domain`: entidades, value objects, regras e eventos de dominio.
- `application`: casos de uso, comandos, queries e orquestracao.
- `infrastructure`: repositorios, mensageria, cache, banco, clients externos e adapters.
- `api`: controllers FastAPI, schemas de entrada/saida e autenticacao.

Dependencias permitidas:

```text
api -> application -> domain
infrastructure -> application/domain
domain -> sem dependencia de framework
```

O `shared kernel` deve conter apenas conceitos estaveis e transversais, como healthcheck, eventos, value objects comuns e formulas aceitas pelo dominio. Regras especificas de um contexto devem permanecer no proprio servico.

## Contextos Delimitados

| Contexto     | Servico                | Responsabilidade                                                     | Agregados principais                           | Eventos publicados                                                    |
| ------------ | ---------------------- | -------------------------------------------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------- |
| Identity     | `auth-service`         | Usuarios, login, perfil e base social.                               | Player, AuthSession                            | `PlayerRegistered`, `PlayerLoggedIn`                                  |
| Cards        | `card-service`         | Cards, colecao, raridade, geracao procedural, unicidade e expiracao. | Card, Deck, CardGenerationBatch                | `CardCreated`, `CardExpired`, `DeckSelected`                          |
| Matchmaking  | `matchmaking-service`  | Filas, pareamento por nivel medio do deck e fallback PvE.            | MatchmakingTicket, QueueEntry                  | `MatchmakingRequested`, `MatchStarted`, `BotMatchCreated`             |
| Gameplay     | `gameplay-service`     | Partidas, rodadas, regras, BOT e validacao anti-cheat.               | Match, Round, BotStrategy                      | `RoundFinished`, `PlayerWonMatch`, `MatchAbandoned`                   |
| Economy      | `economy-service`      | Creditos, loja, compras, renovacao e inventario economico.           | Wallet, CreditLedgerEntry, ShopOffer, Purchase | `CreditsEarned`, `OfferPurchased`, `CardRenewed`                      |
| Ranking      | `ranking-service`      | ELO/MMR, tiers, temporadas e leaderboards.                           | Rating, Leaderboard, Season                    | `PlayerRankUpdated`, `SeasonStarted`, `SeasonFinished`                |
| NFT          | `nft-service`          | Metadados NFT, mint futuro, ownership e integracao Polygon.          | NftMetadata, MintRequest, MarketplaceListing   | `NftMetadataGenerated`, `NFTTransferred`, `MarketplaceListingCreated` |
| Social       | `social-service`       | Amigos, convites, guildas, chat futuro e replay social.              | Friendship, Invite, Guild                      | `FriendInviteSent`, `FriendInviteAccepted`                            |
| Notification | `notification-service` | Push, alertas, convites e mensagens de sistema.                      | Notification, DeliveryAttempt                  | `NotificationQueued`, `NotificationDelivered`                         |

## Relacionamentos Entre Contextos

| Origem      | Destino      | Tipo                | Contrato                                                          |
| ----------- | ------------ | ------------------- | ----------------------------------------------------------------- |
| Web/Mobile  | Auth         | REST                | `POST /auth/register`, `POST /auth/login`                         |
| Web/Mobile  | Cards        | REST                | `GET /cards`, `GET /cards/{id}`, `POST /cards/select-deck`        |
| Web/Mobile  | Matchmaking  | REST                | `POST /matchmaking/find`                                          |
| Web/Mobile  | Gameplay     | REST/WebSocket      | `GET /match/{id}`, `POST /match/{id}/play`, eventos em tempo real |
| Web/Mobile  | Economy      | REST                | `GET /shop/offers`, `POST /shop/buy`                              |
| Web/Mobile  | Ranking      | REST                | `GET /ranking/global`, `GET /ranking/friends`                     |
| Cards       | NFT          | Evento              | `CardCreated` para gerar metadados NFT offline                    |
| Matchmaking | Gameplay     | Evento/REST interno | `MatchStarted` cria sessao jogavel                                |
| Gameplay    | Economy      | Evento              | `PlayerWonMatch` gera creditos                                    |
| Gameplay    | Ranking      | Evento              | `PlayerWonMatch` atualiza rating                                  |
| Ranking     | Notification | Evento              | `PlayerRankUpdated` notifica jogador                              |
| Economy     | Notification | Evento              | `CreditsEarned` e compras notificam jogador                       |

## Regras de Integracao

- Um servico nao acessa tabelas de outro contexto.
- Um servico nao importa codigo de outro servico diretamente.
- Contratos publicos vivem em `packages/api-contracts`.
- Eventos precisam ter nome, versao, produtor, consumidores e payload minimo.
- Integracoes sincronas devem ser usadas para consultas interativas do jogador.
- Integracoes assincronas devem ser usadas para efeitos colaterais, ranking, notificacoes e telemetria.
- Blockchain real permanece atras de feature flag ate o pos-MVP.

## Shared Kernel Inicial

Local: `packages/python/super-trunfo-shared`.

| Modulo      | Uso permitido                                              |
| ----------- | ---------------------------------------------------------- |
| `cards.py`  | Formulas estaveis de nivel, expiracao e hash de unicidade. |
| `events.py` | Estrutura base de evento de dominio.                       |
| `health.py` | Resposta comum de health/readiness.                        |
| `api.py`    | Fabrica comum para cascas FastAPI de servicos.             |

## Contratos de Dominio

O contrato consolidado fica em `packages/api-contracts/domain/domain-contracts.yaml` e deve ser atualizado quando um agregado, comando, query ou evento publico mudar.
