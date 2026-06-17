# Super Trunfo NFT Game Platform

Monorepo publico para evoluir um jogo competitivo de cards nos moldes do Super Trunfo, com base na arquitetura DDD/hexagonal descrita em `docs/Arquitetura Jogo Super Trunfo Nft Ddd.pdf`.

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
- [Mapa DDD e arquitetura hexagonal](docs/architecture/ddd-context-map.md)
- [Ambiente local](docs/operations/local-development.md)
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

## Subir Ambiente Localhost

Execute os comandos abaixo a partir da raiz do repositorio.

### Pre-requisitos

- Docker com Compose v2.
- Node.js 22 e pnpm 9, caso queira executar validacoes do monorepo fora dos containers.

### Validar o Docker Compose

```bash
pnpm local:check
docker compose -f infra/docker/compose.yaml config
```

### Subir todos os servicos

```bash
docker compose -f infra/docker/compose.yaml up --build
```

### Executar o app mobile

```bash
cd apps/mobile
flutter pub get
flutter run \
  --dart-define=SUPER_TRUNFO_ENV=local \
  --dart-define=SUPER_TRUNFO_API_BASE_URL=http://10.0.2.2:8001
```

O uso de HTTP deve ficar restrito ao ambiente `local`, para acesso ao backend no emulador Android.

Para apontar para outro ambiente:

```bash
flutter run \
  --dart-define=SUPER_TRUNFO_ENV=staging \
  --dart-define=SUPER_TRUNFO_API_BASE_URL=https://staging.super-trunfo.app
```

Para subir em background:

```bash
docker compose -f infra/docker/compose.yaml up --build -d
```

### Verificar status e logs

```bash
docker compose -f infra/docker/compose.yaml ps
docker compose -f infra/docker/compose.yaml logs -f
```

Healthcheck rapido do servico de autenticacao:

```bash
curl http://localhost:8001/health
```

### Acessos locais

| Componente           | URL/porta                      | Uso                          |
| -------------------- | ------------------------------ | ---------------------------- |
| Web                  | `http://localhost:3000`        | App Next.js                  |
| Auth service         | `http://localhost:8001/health` | Identity, cadastro e login   |
| Card service         | `http://localhost:8002/health` | Cards e colecao              |
| Matchmaking service  | `http://localhost:8003/health` | Filas e pareamento           |
| Gameplay service     | `http://localhost:8004/health` | Partidas e rodadas           |
| Economy service      | `http://localhost:8005/health` | Creditos e loja              |
| Ranking service      | `http://localhost:8006/health` | Rating e leaderboard         |
| NFT service          | `http://localhost:8007/health` | Metadados NFT                |
| Social service       | `http://localhost:8008/health` | Amigos e convites            |
| Notification service | `http://localhost:8009/health` | Push e alertas               |
| PostgreSQL           | `localhost:5432`               | Banco transacional           |
| Redis                | `localhost:6379`               | Cache, ranking e matchmaking |
| RabbitMQ             | `localhost:5672`               | Eventos de dominio           |
| RabbitMQ Management  | `http://localhost:15672`       | Console local                |
| OpenSearch           | `http://localhost:9200`        | Busca e indexacao preparada  |

Credenciais locais:

| Componente | Usuario        | Senha          | Banco          |
| ---------- | -------------- | -------------- | -------------- |
| PostgreSQL | `super_trunfo` | `super_trunfo` | `super_trunfo` |
| RabbitMQ   | `super_trunfo` | `super_trunfo` | -              |

### Parar o ambiente

```bash
docker compose -f infra/docker/compose.yaml down
```

Para apagar tambem os volumes locais, incluindo dados do PostgreSQL:

```bash
docker compose -f infra/docker/compose.yaml down --volumes
```

Mais detalhes estao em [Ambiente local](docs/operations/local-development.md).
