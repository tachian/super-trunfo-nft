# ADR 0001 - Arquitetura Base

## Status

Aceita

## Contexto

O produto precisa suportar jogo competitivo de cards, matchmaking em tempo real, economia interna, ranking, social, notificacoes e uma evolucao futura para NFTs e marketplace. O PDF recomenda DDD, arquitetura hexagonal, microsservicos, FastAPI, PostgreSQL, Redis, mensageria, OpenSearch, Docker, Kubernetes, Terraform, GitHub Actions e ArgoCD.

## Decisao

Adotaremos um monorepo com:

- servicos FastAPI separados por contexto de dominio;
- shared kernel Python para objetos de valor, eventos, healthcheck e convencoes comuns;
- contratos OpenAPI e eventos em `packages/api-contracts`;
- Next.js para web;
- Flutter para mobile;
- smart contracts isolados em `smart-contracts`;
- infraestrutura declarativa em Docker Compose, Kubernetes, Terraform e ArgoCD;
- CI/CD via GitHub Actions;
- padroes de engenharia em `docs/architecture/service-engineering-standards.md`, cobrindo DDD, SOLID, logs estruturados, mascaramento LGPD e quality gates.

## Contextos iniciais

- Identity: usuarios, login, perfil, amigos e social.
- Cards: cards, colecao, raridade, geracao, expiracao e metadados NFT.
- Gameplay: partida, rodada, regras, BOT e validacao server-side.
- Matchmaking: filas, pareamento por nivel medio de deck e fallback PvE.
- Economy: creditos, loja, compras, inventario e renovacao.
- Ranking: ELO/MMR, tiers, temporadas e leaderboards.
- NFT: mint, metadados, ownership e integracao Polygon.
- Social: amigos, convites, guildas, chat e replay.
- Notification: push, alertas e eventos.

## Consequencias

- Servicos podem evoluir independentemente, mantendo limites de dominio claros.
- Todos os servicos precisam manter estrutura DDD/hexagonal uniforme para reduzir divergencia entre contextos.
- Codigo novo deve respeitar SOLID e expor dependencias externas por portas/adapters.
- Logs de requests, responses e integracoes externas passam a ser obrigatorios, sempre com mascaramento de dados sensiveis.
- O monorepo facilita padronizacao, contratos e CI compartilhado.
- O CI deve bloquear merge quando lint, PEP8/Ruff, duplicacao, testes, contratos ou scans de vulnerabilidade falharem.
- Blockchain fica atras de feature flag para preservar foco do MVP.
- A complexidade operacional aumenta, entao a primeira sprint inclui automacao, observabilidade e ambiente local.
