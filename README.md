# Super Trunfo NFT Game Platform

Monorepo publico para evoluir um jogo competitivo de cards nos moldes do Super Trunfo, com base na arquitetura DDD/hexagonal descrita em `../doc/Arquitetura Jogo Super Trunfo Nft Ddd.pdf`.

## Objetivo

Criar uma plataforma multiplataforma para Web, Android e iOS com partidas PvP/PvE, matchmaking por nivel de deck, loja, economia por creditos, ranking, geracao procedural de cards e evolucao posterior para NFTs em Polygon.

## Estrutura

```text
apps/
  services/          FastAPI services por contexto de dominio
  web/               Next.js web app
  mobile/            Flutter mobile app
packages/
  api-contracts/     OpenAPI/event contracts compartilhados
  python/            Shared kernel Python
infra/
  docker/            Dockerfiles e compose local
  k8s/               Manifests Kubernetes base
  terraform/         Infraestrutura AWS/EKS/RDS/Redis/S3
  argocd/            GitOps applications
smart-contracts/     ERC-721 e marketplace on-chain
docs/
  project/           Roadmap, backlog, sprints e rastreabilidade
  adr/               Architecture Decision Records
```

## Roadmap MVP

1. Fundacao do monorepo, CI/CD, padroes DDD e ambiente local.
2. Autenticacao, perfil, deck inicial e creditos iniciais.
3. Cards, geracao procedural, unicidade e expiracao.
4. Gameplay basico, BOT e validacao server-side.
5. Matchmaking, ranking, loja e economia.
6. Web/mobile MVP.
7. Preparacao NFT/marketplace atras de feature flags.
8. Social, notificacoes, observabilidade e release candidate.

## Documentacao de projeto

- [Visao do produto](docs/project/product-vision.md)
- [Plano de implementacao do MVP](docs/project/mvp-implementation-plan.md)
- [Roadmap](docs/project/roadmap.md)
- [Backlog](docs/project/backlog.md)
- [Sprints e tarefas](docs/project/sprints.md)
- [Rastreabilidade de requisitos](docs/project/requirements-traceability.md)
- [ADR 0001 - Arquitetura base](docs/adr/0001-base-architecture.md)

## Politica de commits

Cada tarefa concluida deve gerar commit pequeno e rastreavel, usando o ID da tarefa no prefixo:

```text
ST-001: scaffold monorepo foundation
ST-201: implement card uniqueness hash
```

Ao final de cada tarefa, o commit deve ser enviado para o GitHub.
