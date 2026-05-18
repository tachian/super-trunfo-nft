# Plano de Implementacao do MVP

Fonte principal: `docs/Arquitetura Jogo Super Trunfo Nft Ddd.pdf`.

## Objetivo do MVP

Validar o ciclo principal do jogo antes de ativar blockchain real:

1. jogador cria conta e acessa perfil;
2. jogador recebe deck inicial balanceado;
3. jogador visualiza colecao e escolhe 10 cards;
4. matchmaking busca oponente por nivel medio do deck;
5. se nao houver jogador compativel, o sistema cria BOT equivalente;
6. jogador disputa uma partida completa;
7. resultado atualiza creditos, rating e ranking;
8. jogador usa creditos na loja para comprar ou renovar cards.

## Decisoes de Escopo

### Dentro do MVP

- Web app em Next.js como primeira experiencia jogavel.
- Mobile Flutter como shell funcional com navegacao principal e smoke tests.
- Backend FastAPI com servicos por contexto DDD.
- PostgreSQL para dados transacionais.
- Redis para cache, ranking e matchmaking.
- RabbitMQ para eventos de dominio.
- OpenSearch preparado para busca de cards, ainda com uso restrito.
- CI/CD completo com testes, build Docker, scan de seguranca e GitOps.
- Feature flags desde o inicio.
- Metadados NFT gerados offline para preparar a evolucao futura.

### Fora do MVP

- Mint real em Polygon.
- Marketplace secundario on-chain.
- Trocas entre jogadores.
- Wallet custodial em producao.
- Guildas, chat e eventos sazonais completos.
- Monetizacao paga, battle pass e torneios pagos.

## Marcos de Entrega

| Marco | Resultado esperado                                   | Sprint alvo |
| ----- | ---------------------------------------------------- | ----------- |
| M0    | Monorepo, CI/CD, ambiente local e servicos base.     | Sprint 0    |
| M1    | Usuario cadastra, loga e recebe primeiro deck.       | Sprint 1    |
| M2    | Cards procedurais unicos e colecao consultavel.      | Sprint 2    |
| M3    | Partida PvE completa com BOT e regras server-side.   | Sprint 3    |
| M4    | Matchmaking PvP/PvE, ranking e economia funcionando. | Sprint 4    |
| M5    | Web MVP jogavel ponta a ponta.                       | Sprint 5    |
| M6    | Hardening, observabilidade e release candidate.      | Sprint 6    |

## Sprint 0 - Fundacao Tecnica

Periodo sugerido: 18 de maio de 2026 a 29 de maio de 2026.

Objetivo: criar a base do projeto para que as proximas sprints entreguem produto sem retrabalho estrutural.

### Historias

| ID      | Historia                                                                                                      | Criterios de aceite                                                                                                                                                                                                       |
| ------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MVP-001 | Como desenvolvedor, quero um monorepo padronizado para organizar apps, servicos, contratos, infra e docs.     | Estrutura raiz contem `apps`, `packages`, `infra`, `smart-contracts` e `docs`; README explica a estrutura; comandos principais estao no `package.json` e `Makefile`.                                                      |
| MVP-002 | Como desenvolvedor, quero servicos FastAPI baseados em contextos DDD para evoluir cada dominio separadamente. | Servicos `auth`, `card`, `matchmaking`, `gameplay`, `economy`, `ranking`, `nft`, `social` e `notification` possuem healthcheck, readiness e rota de contexto.                                                             |
| MVP-003 | Como desenvolvedor, quero contratos compartilhados para alinhar frontend, backend e eventos.                  | OpenAPI inicial cobre auth, cards, matchmaking, match, shop e ranking; catalogo de eventos inclui `CardCreated`, `MatchStarted`, `RoundFinished`, `PlayerWonMatch`, `CreditsEarned`, `CardExpired` e `PlayerRankUpdated`. |
| MVP-004 | Como desenvolvedor, quero ambiente local completo para subir dependencias do MVP.                             | Docker Compose sobe Postgres, Redis, RabbitMQ, OpenSearch, web e servicos; portas locais documentadas; healthchecks basicos configurados.                                                                                 |
| MVP-005 | Como time de produto, quero CI/CD desde a primeira sprint para manter qualidade e entrega continua.           | GitHub Actions executa lint, testes, build Docker, scan de seguranca e deploy GitOps controlado para staging/producao.                                                                                                    |

### Saida da sprint

Repositario pronto, pipeline ativo e ambiente local capaz de executar o esqueleto da plataforma.

## Sprint 1 - Identity, Perfil e Primeiro Acesso

Periodo sugerido: 1 de junho de 2026 a 12 de junho de 2026.

Objetivo: permitir que um jogador entre no jogo e receba os recursos iniciais.

### Historias

| ID      | Historia                                                                                        | Criterios de aceite                                                                                                                                             |
| ------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MVP-101 | Como jogador, quero criar uma conta com nickname e credenciais para acessar o jogo.             | `POST /auth/register` cria jogador unico; nickname respeita limite de 50 caracteres; senha ou provedor OAuth e validado; evento `PlayerRegistered` e publicado. |
| MVP-102 | Como jogador, quero fazer login para receber um token valido.                                   | `POST /auth/login` retorna JWT; token contem player id e expiracao; tentativas invalidas retornam erro seguro; logs nao expoem credenciais.                     |
| MVP-103 | Como jogador, quero ver meu perfil inicial para acompanhar rating e creditos.                   | Perfil retorna id, nickname, rating inicial, creditos iniciais e data de criacao; endpoint exige autenticacao.                                                  |
| MVP-104 | Como jogador novo, quero receber 9 cards iniciais balanceados e creditos para comprar o decimo. | Primeiro acesso cria 9 cards sem lendarios, com raridade/atributos limitados; creditos iniciais sao registrados em ledger; operacao e idempotente.              |
| MVP-105 | Como operador, quero auditar cadastro e login para investigar abuso.                            | Eventos de login/cadastro sao persistidos ou publicados; falhas repetidas geram metrica; endpoint possui rate limit basico.                                     |

### Saida da sprint

Jogador consegue se registrar, logar, consultar perfil e receber deck inicial.

## Sprint 2 - Cards, Colecao e Geracao Procedural

Periodo sugerido: 15 de junho de 2026 a 26 de junho de 2026.

Objetivo: implementar o dominio de cards com unicidade, raridade, expiracao e colecao.

### Historias

| ID      | Historia                                                                                        | Criterios de aceite                                                                                                                          |
| ------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| MVP-201 | Como jogador, quero listar meus cards para montar meu deck.                                     | `GET /cards` retorna cards do jogador autenticado; resposta inclui atributos, nivel, raridade, familia, validade e status de expiracao.      |
| MVP-202 | Como jogador, quero abrir detalhes de um card para comparar atributos.                          | `GET /cards/{id}` retorna somente cards pertencentes ao jogador; cards inexistentes ou de outro dono retornam erro adequado.                 |
| MVP-203 | Como sistema, quero calcular nivel do card pela soma dos atributos para apoiar matchmaking.     | Nivel e calculado por `speed + strength + intelligence + resistance + rarity`; teste unitario cobre a formula.                               |
| MVP-204 | Como sistema, quero impedir cards totalmente identicos para preservar unicidade.                | Hash SHA-256 usa nome e atributos principais; se hash ja existir, a geracao regenera card; restricao e testada em unidade e integracao.      |
| MVP-205 | Como sistema, quero expirar cards com base na raridade para controlar economia e balanceamento. | Formula usa base de 365 dias e bonus `int((rarity - 50) * 1.2)`; cards expirados nao podem entrar no deck ativo.                             |
| MVP-206 | Como operador, quero um worker de geracao procedural para abastecer a loja e decks iniciais.    | Worker gera cards conforme distribuicao comum 50%, raro 30%, epico 15%, lendario 5%; publica `CardCreated`; indexa dados basicos para busca. |
| MVP-207 | Como time futuro de blockchain, quero metadados NFT offline para preparar mint pos-MVP.         | JSON de metadados segue padrao ERC-721 com nome, descricao, imagem e atributos; feature de mint permanece desligada.                         |

### Saida da sprint

Colecao funcional, cards unicos, expiracao aplicada e geracao procedural preparada.

## Sprint 3 - Deck, Gameplay e BOT

Periodo sugerido: 29 de junho de 2026 a 10 de julho de 2026.

Objetivo: entregar partida completa contra BOT com logica autoritativa no backend.

### Historias

| ID      | Historia                                                                                    | Criterios de aceite                                                                                                                                                |
| ------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| MVP-301 | Como jogador, quero selecionar 10 cards validos para formar meu deck.                       | `POST /cards/select-deck` exige 10 cards; valida propriedade, expiracao e duplicidade; calcula nivel medio do deck.                                                |
| MVP-302 | Como sistema, quero criar uma partida para controlar jogadores, rodadas, status e vencedor. | Entidade `Match` possui id, player1, player2/BOT, rounds, winner e status; estados validos sao testados.                                                           |
| MVP-303 | Como sistema, quero registrar cada rodada para permitir replay auditavel.                   | Entidade `Round` guarda atributo escolhido, cards usados, vencedor e timestamp; cada jogada gera trilha auditavel.                                                 |
| MVP-304 | Como jogador, quero escolher um atributo do meu card para disputar a rodada.                | `POST /match/{id}/play` aceita somente atributos validos; rejeita card fora do deck, rodada repetida ou partida encerrada.                                         |
| MVP-305 | Como jogador, quero enfrentar um BOT quando nao houver oponente humano.                     | BOT recebe deck equivalente; escolhe melhor atributo de forma probabilistica; resultado e indistinguivel do fluxo normal de partida.                               |
| MVP-306 | Como sistema, quero calcular vencedor da partida por maior numero de rodadas vencidas.      | Vitoria de rodada soma 1 ponto; partida termina quando todas as cartas validas forem usadas ou regra definida for satisfeita; evento `PlayerWonMatch` e publicado. |

### Saida da sprint

Fluxo PvE completo: selecionar deck, criar partida, jogar rodadas, concluir partida e publicar resultado.

## Sprint 4 - Matchmaking, Economia e Ranking

Periodo sugerido: 13 de julho de 2026 a 24 de julho de 2026.

Objetivo: fechar progressao competitiva com matchmaking, recompensas, loja e ranking.

### Historias

| ID      | Historia                                                                                      | Criterios de aceite                                                                                                                          |
| ------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| MVP-401 | Como jogador, quero buscar partida com adversario de nivel semelhante para ter disputa justa. | `POST /matchmaking/find` usa nivel medio do deck; tolerancia inicial e +/-20 pontos; filas Redis existem por tier.                           |
| MVP-402 | Como jogador, quero cair automaticamente em PvE se nao houver oponente compativel.            | Apos timeout configuravel, matchmaking cria BOT equivalente; evento `MatchStarted` e publicado.                                              |
| MVP-403 | Como jogador, quero receber creditos ao vencer uma partida para progredir.                    | Vitoria concede 1 credito; derrota concede 0; ledger impede duplicidade; evento `CreditsEarned` e publicado.                                 |
| MVP-404 | Como jogador, quero comprar cards na loja usando creditos.                                    | `GET /shop/offers` lista ofertas ativas; `POST /shop/buy` valida saldo, oferta e expiracao; inventario e saldo sao atualizados atomicamente. |
| MVP-405 | Como jogador, quero ver meu rating atualizado apos a partida.                                 | Ranking usa formula ELO/MMR simplificada; tiers Bronze, Silver, Gold, Platinum e Diamond sao derivados da pontuacao.                         |
| MVP-406 | Como jogador, quero consultar ranking global para comparar desempenho.                        | `GET /ranking/global` retorna leaderboard paginado e cacheado; ranking atualiza apos `PlayerWonMatch`.                                       |
| MVP-407 | Como jogador, quero ranking de amigos preparado para evoluir social.                          | `GET /ranking/friends` retorna vazio/planejado quando nao houver amigos; contrato fica estavel para a sprint social.                         |

### Saida da sprint

Partidas PvP/PvE entram no mesmo ciclo de recompensa, ranking e loja.

## Sprint 5 - Web MVP e Smoke Mobile

Periodo sugerido: 27 de julho de 2026 a 7 de agosto de 2026.

Objetivo: tornar o MVP jogavel pela web e deixar o mobile preparado para evolucao incremental.

### Historias

| ID      | Historia                                                                   | Criterios de aceite                                                                                                                 |
| ------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| MVP-501 | Como jogador, quero acessar o web app e autenticar para entrar no jogo.    | Tela de login/cadastro integrada com `auth-service`; token e armazenado de forma segura; logout limpa sessao.                       |
| MVP-502 | Como jogador, quero gerenciar minha colecao e deck pelo web app.           | Interface lista cards, mostra atributos, validade e raridade; jogador seleciona 10 cards; erros de validacao aparecem claramente.   |
| MVP-503 | Como jogador, quero iniciar matchmaking pela web.                          | Botao de buscar partida chama `matchmaking-service`; UI mostra status de fila, fallback PvE e partida criada.                       |
| MVP-504 | Como jogador, quero jogar uma partida completa pela web.                   | Mesa exibe card atual, atributos, placar, rodada e vencedor; cada acao chama backend; estados de loading/erro existem.              |
| MVP-505 | Como jogador, quero ver loja, creditos e ranking no web app.               | UI mostra saldo, ofertas, compra, ranking global e posicao do jogador; dados atualizam apos partida/compra.                         |
| MVP-506 | Como stakeholder, quero um app mobile shell para validar navegacao futura. | Flutter possui rotas principais, tela de dashboard, tema do produto e teste de widget; integracao total fica fora do MVP web-first. |
| MVP-507 | Como time, quero teste E2E smoke para o fluxo principal.                   | CI executa login, consulta deck, matchmaking, jogada basica e compra mockada/ambiente staging.                                      |

### Saida da sprint

MVP web jogavel ponta a ponta e mobile preparado sem bloquear validacao do gameplay.

## Sprint 6 - Observabilidade, Seguranca e Release Candidate

Periodo sugerido: 10 de agosto de 2026 a 21 de agosto de 2026.

Objetivo: estabilizar o MVP para demonstracao, staging e inicio de beta fechado.

### Historias

| ID      | Historia                                                                            | Criterios de aceite                                                                                                            |
| ------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| MVP-601 | Como operador, quero metricas de retencao, abandono e win rate para avaliar o jogo. | Eventos medem login, partida iniciada, partida concluida, abandono, win rate por card e tempo de matchmaking.                  |
| MVP-602 | Como operador, quero logs e traces correlacionados para investigar problemas.       | Servicos propagam correlation id; OpenTelemetry configurado; dashboards iniciais para health, latencia e erros.                |
| MVP-603 | Como operador, quero monitorar economia para evitar inflacao e abuso.               | Metricas de creditos ganhos, creditos gastos, compras, cards expirados e saldo medio por jogador.                              |
| MVP-604 | Como sistema, quero validacoes anti-cheat no backend para proteger partidas.        | Backend rejeita alteracao de placar, jogada repetida, card invalido e atributo invalido; replay auditavel disponivel.          |
| MVP-605 | Como operador, quero rate limit e hardening basico de seguranca.                    | Endpoints sensiveis possuem rate limit; JWT usa segredo externo; scan de seguranca roda no CI; checklist OWASP MVP preenchido. |
| MVP-606 | Como time de entrega, quero release candidate em staging.                           | CD publica imagens, ArgoCD sincroniza staging, smoke tests passam e runbook de rollback existe.                                |
| MVP-607 | Como PO, quero criterio claro de aceite do MVP.                                     | Checklist final confirma fluxo completo, metricas basicas, bugs criticos zerados e decisoes pos-MVP documentadas.              |

### Saida da sprint

Release candidate do MVP pronto para beta fechado e demonstracao.

## Backlog Pos-MVP Priorizado

| Prioridade | Item                               | Motivo                                                 |
| ---------- | ---------------------------------- | ------------------------------------------------------ |
| P1         | NFT real em Polygon com ERC-721    | Ativa propriedade digital depois de validar gameplay.  |
| P1         | Wallet custodial                   | Reduz friccao para jogadores nao cripto.               |
| P1         | Marketplace secundario             | Expande economia e monetizacao.                        |
| P2         | Amigos e convites completos        | Aumenta retencao e ranking social.                     |
| P2         | Temporadas de 30-90 dias           | Cria ciclos de progressao e recompensas.               |
| P2         | Balanceamento por analytics        | Ajusta win rate, frequencia de uso e cards dominantes. |
| P3         | Guildas, chat e eventos dinamicos  | Expande comunidade depois do core competitivo.         |
| P3         | Modos torneio, draft e cooperativo | Amplia variedade de gameplay.                          |

## Definition of Ready

- Historia ligada a uma sprint e a um contexto DDD.
- Criterios de aceite testaveis.
- APIs/eventos impactados identificados.
- Dados persistidos definidos.
- Riscos de seguranca, anti-cheat e economia avaliados.

## Definition of Done

- Codigo implementado no servico/app correto.
- Testes unitarios e de integracao relevantes adicionados.
- Contratos OpenAPI/eventos atualizados quando necessario.
- Observabilidade minima adicionada para o fluxo.
- Docker/CI atualizado se o runtime mudou.
- Commit com ID da historia ou tarefa.
- Push para GitHub ao final da historia.

## Riscos e Mitigacoes

| Risco                  | Impacto               | Mitigacao                                                                    |
| ---------------------- | --------------------- | ---------------------------------------------------------------------------- |
| Gameplay desbalanceado | Baixa retencao        | Medir win rate por card, uso por raridade e abandono desde Sprint 6.         |
| Matchmaking lento      | Frustracao do jogador | Fallback PvE com BOT equivalente e tolerancia configuravel.                  |
| Economia inflacionada  | Loja perde valor      | Ledger de creditos, telemetria de saldo e ajustes por feature flag.          |
| Fraude em partidas     | Ranking sem confianca | Logica server-side, replay auditavel, rate limit e validacao de cada rodada. |
| Blockchain antecipada  | Atraso no MVP         | Manter NFT real fora do MVP e gerar apenas metadados offline.                |

## Criterios de Aceite do MVP

- Jogador novo consegue registrar, logar e receber deck inicial.
- Jogador consegue selecionar deck valido de 10 cards.
- Jogador consegue concluir uma partida PvE e ao menos um fluxo PvP em staging.
- Vitoria atualiza creditos e rating.
- Loja permite comprar card/oferta com creditos.
- Ranking global reflete resultado de partidas.
- Web app executa o fluxo completo.
- CI/CD passa em `main`.
- Staging tem deploy reproduzivel.
- Metricas basicas de jogo, economia e matchmaking estao disponiveis.
