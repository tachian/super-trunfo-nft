# Ambiente Local

O ambiente local da Sprint 0 usa Docker Compose para subir as dependencias do MVP e os servicos de exemplo.

## Pre-requisitos

- Docker com Compose v2.
- Node.js 22 e pnpm 9 para comandos do monorepo fora dos containers.
- Python 3.12 para testes locais dos servicos.

## Comandos

Validar a configuracao do Compose:

```bash
pnpm local:check
```

Subir todo o ambiente:

```bash
docker compose -f infra/docker/compose.yaml up --build
```

Encerrar o ambiente:

```bash
docker compose -f infra/docker/compose.yaml down
```

Remover volumes locais quando precisar reiniciar banco e filas do zero:

```bash
docker compose -f infra/docker/compose.yaml down --volumes
```

## Portas Locais

| Componente           | URL/porta                      | Uso                          |
| -------------------- | ------------------------------ | ---------------------------- |
| Web                  | `http://localhost:3000`        | Shell web Next.js            |
| Auth service         | `http://localhost:8001/health` | Identity e login             |
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
| RabbitMQ Management  | `http://localhost:15672`       | Console local `super_trunfo` |
| OpenSearch           | `http://localhost:9200`        | Busca e indexacao preparada  |

## Regras do Ambiente

- Servicos FastAPI aguardam Postgres, Redis, RabbitMQ e OpenSearch ficarem saudaveis antes de iniciar quando houver dependencia.
- Web aguarda os servicos principais ficarem saudaveis.
- Healthchecks dos servicos usam `/health`.
- Credenciais locais sao somente para desenvolvimento e nao devem ser reutilizadas em staging/producao.
- `FEATURE_NFT_ENABLED=false` mantem blockchain real desligada no MVP.
