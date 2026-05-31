# Sprints e Tarefas

Planejamento inicial com sprints quinzenais, iniciando em 18 de maio de 2026.

## Sprint 0 - Fundacao do Projeto

Periodo: 18 de maio de 2026 a 29 de maio de 2026

Objetivo: deixar o monorepo pronto para desenvolvimento colaborativo e entregas continuas.

| ID     | Tarefa                                            | Criterios de aceite                                                                                                                                   |
| ------ | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| ST-001 | Criar monorepo publico com estrutura base         | Repositorio criado, README, licenca, pastas principais e convencao de commits documentados.                                                           |
| ST-002 | Criar backlog, roadmap, sprints e rastreabilidade | Documentos em `docs/project` com epicos, tarefas, datas e origem nos requisitos do PDF.                                                               |
| ST-003 | Definir arquitetura DDD/hexagonal e shared kernel | ADR criado, contextos mapeados e contratos de dominio inicializados.                                                                                  |
| ST-004 | Criar pipeline CI/CD base                         | GitHub Actions validando lint, PEP8/Ruff, duplicacao, testes, build Docker, scan, SonarCloud quando configurado e deploy staging/producao controlado. |
| ST-005 | Criar ambiente local                              | Docker Compose com Postgres, Redis, RabbitMQ, OpenSearch e servicos de exemplo.                                                                       |

## Sprint 1 - Identity e Onboarding

Periodo: 1 de junho de 2026 a 12 de junho de 2026

Objetivo: permitir cadastro, login e primeira experiencia do jogador.

| ID     | Tarefa                              | Criterios de aceite                                                        |
| ------ | ----------------------------------- | -------------------------------------------------------------------------- |
| ST-101 | Implementar registro e login        | APIs `POST /auth/register` e `POST /auth/login`, JWT e testes de contrato. |
| ST-102 | Criar perfil do jogador             | Perfil com nickname, rating inicial, creditos e metadados de social login. |
| ST-103 | Conceder deck inicial               | Primeiro acesso gera 9 cards balanceados e creditos para o decimo card.    |
| ST-104 | Integrar tela inicial web           | Fluxo web de login, perfil e estado autenticado.                           |
| ST-105 | Adicionar auditoria de autenticacao | Eventos `PlayerRegistered` e `PlayerLoggedIn` publicados.                  |

## Sprint 2 - Cards e Geracao Procedural

Periodo: 15 de junho de 2026 a 26 de junho de 2026

Objetivo: implementar o dominio de cards e a geracao de cartas unicas.

| ID     | Tarefa                              | Criterios de aceite                                                       |
| ------ | ----------------------------------- | ------------------------------------------------------------------------- |
| ST-201 | Modelar agregado Card               | Entidade com UUID, atributos, raridade, familia, owner, nivel e validade. |
| ST-202 | Garantir unicidade por hash SHA-256 | Dois cards identicos sao bloqueados e a geracao regenera atributos.       |
| ST-203 | Implementar formula de expiracao    | Validade baseada em 365 dias e bonus por raridade.                        |
| ST-204 | Criar worker de geracao procedural  | Worker periodico cria cards, persiste, indexa e publica `CardCreated`.    |
| ST-205 | Preparar metadados NFT offline      | JSON de metadados gerado sem mint on-chain no MVP.                        |

## Sprint 3 - Gameplay Basico e BOT

Periodo: 29 de junho de 2026 a 10 de julho de 2026

Objetivo: entregar partidas jogaveis com regras autoritativas no backend.

| ID     | Tarefa                        | Criterios de aceite                                                                 |
| ------ | ----------------------------- | ----------------------------------------------------------------------------------- |
| ST-301 | Selecionar deck de 10 cards   | API `POST /cards/select-deck` valida propriedade, validade e tamanho do deck.       |
| ST-302 | Modelar Match e Round         | Partida guarda jogadores, rodadas, atributo selecionado, placar, vencedor e status. |
| ST-303 | Implementar estrategia do BOT | BOT escolhe melhor atributo probabilisticamente e usa deck equivalente.             |
| ST-304 | Validar jogadas server-side   | Backend rejeita card invalido, atributo invalido, replay e alteracao de placar.     |
| ST-305 | Criar APIs de partida         | `GET /match/{id}` e `POST /match/{id}/play` com testes unitarios e integracao.      |

## Sprint 4 - Matchmaking e Tempo Real

Periodo: 13 de julho de 2026 a 24 de julho de 2026

Objetivo: parear jogadores por nivel medio do deck e transmitir eventos da partida.

| ID     | Tarefa                         | Criterios de aceite                                                    |
| ------ | ------------------------------ | ---------------------------------------------------------------------- |
| ST-401 | Criar filas Redis por tier     | Filas `queue:bronze`, `queue:silver` e `queue:gold` configuradas.      |
| ST-402 | Parear por tolerancia de nivel | Busca oponente com nivel medio do deck em faixa de +/-20 pontos.       |
| ST-403 | Criar fallback PvE             | Se nao houver oponente compativel, cria BOT equivalente.               |
| ST-404 | Publicar eventos WebSocket     | Eventos de rodada, atributo escolhido, resultado e ranking atualizado. |
| ST-405 | Criar teste de carga inicial   | Cenario simula busca de partidas e mede tempo de pareamento.           |

## Sprint 5 - Economia, Loja e Ranking

Periodo: 27 de julho de 2026 a 7 de agosto de 2026

Objetivo: fechar ciclo de progressao, recompensas e competitividade.

| ID     | Tarefa                             | Criterios de aceite                                                   |
| ------ | ---------------------------------- | --------------------------------------------------------------------- |
| ST-501 | Implementar creditos por resultado | Vitoria concede 1 credito, derrota 0, com evento `CreditsEarned`.     |
| ST-502 | Criar loja de cards                | `GET /shop/offers` e `POST /shop/buy`, ofertas com expiracao e preco. |
| ST-503 | Implementar ranking ELO/MMR        | Formula simplificada atualiza rating apos partida.                    |
| ST-504 | Criar ranking global e amigos      | `GET /ranking/global` e `GET /ranking/friends` com cache.             |
| ST-505 | Telemetria economica               | Medir compras, saldos, win streaks, abuso e inflacao.                 |

## Sprint 6 - Apps Web e Mobile MVP

Periodo: 10 de agosto de 2026 a 21 de agosto de 2026

Objetivo: permitir jogar o fluxo MVP nas interfaces finais.

| ID     | Tarefa                      | Criterios de aceite                                                       |
| ------ | --------------------------- | ------------------------------------------------------------------------- |
| ST-601 | Criar shell Next.js         | Aplicacao web com rotas de login, colecao, deck, partida, loja e ranking. |
| ST-602 | Criar shell Flutter         | Aplicacao mobile com navegacao equivalente e configuracao por ambiente.   |
| ST-603 | Implementar colecao e deck  | UI lista cards, filtros por raridade/familia e selecao de deck.           |
| ST-604 | Implementar mesa de partida | UI exibe cartas, atributo selecionado, placar, rodada e resultado.        |
| ST-605 | Criar smoke E2E             | Fluxo login, deck, matchmaking, partida e compra executado em CI.         |

## Sprint 7 - NFT e Marketplace Readiness

Periodo: 24 de agosto de 2026 a 4 de setembro de 2026

Objetivo: preparar blockchain e marketplace como capacidade opcional pos-MVP.

| ID     | Tarefa                         | Criterios de aceite                                                           |
| ------ | ------------------------------ | ----------------------------------------------------------------------------- |
| ST-701 | Criar contrato ERC-721 base    | Contrato compila, mint controlado e eventos principais definidos.             |
| ST-702 | Desenhar wallet custodial      | ADR com onboarding, seguranca, custodia e migracao futura.                    |
| ST-703 | Modelar marketplace            | Entidade `MarketplaceListing`, status, preco, expiracao e historico.          |
| ST-704 | Modelar trades                 | Eventos `TradeCreated`, `TradeAccepted`, `TradeCancelled` e `NFTTransferred`. |
| ST-705 | Controlar NFT por feature flag | Features de blockchain desligadas por padrao no MVP.                          |

## Sprint 8 - Social, Notificacoes e Release Candidate

Periodo: 7 de setembro de 2026 a 18 de setembro de 2026

Objetivo: aumentar retencao e preparar operacao em producao.

| ID     | Tarefa                        | Criterios de aceite                                                                                        |
| ------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------- |
| ST-801 | Implementar amigos e convites | Jogador envia, aceita e recusa convites.                                                                   |
| ST-802 | Implementar notificacoes      | Push/in-app para convite, partida, loja, ranking e eventos.                                                |
| ST-803 | Criar estrutura de temporadas | Duracao configuravel, reset parcial e recompensas planejadas.                                              |
| ST-804 | Hardening de seguranca        | Rate limit, validacao server-side, logs mascarados LGPD, secret scanning, quality gates e checklist OWASP. |
| ST-805 | Preparar release candidate    | Ambiente staging validado, dashboards ativos, runbooks e rollback.                                         |
