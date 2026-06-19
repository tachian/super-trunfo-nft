# Release Candidate

Este runbook prepara o ST-805: release candidate do MVP em staging, com dashboards ativos, smoke tests e decisao de go/no-go.

## Pre-flight

Execute a partir da raiz do repositorio:

```bash
pnpm install --frozen-lockfile
pnpm release:check
pnpm format:check
pnpm quality:duplicates
pnpm python:test
pnpm lint
pnpm test
pnpm build
```

Antes de acionar CD, confirme:

- PRs das tasks da Sprint 8 estao mergeados em `main`.
- `SONAR_ENABLED=true` e `SONAR_TOKEN` configurados quando o quality gate SonarCloud estiver habilitado.
- `KUBE_CONFIG` aponta para o cluster correto de staging.
- `SUPER_TRUNFO_HSTS_ENABLED=true` apenas quando o ingress de staging estiver em HTTPS.
- Feature flag `FEATURE_NFT_ENABLED=false` para o MVP.

## Staging Validation

Dispare o CD manualmente para staging:

```bash
gh workflow run CD --ref main -f environment=staging
```

Depois da sincronizacao do ArgoCD:

```bash
kubectl -n argocd get application super-trunfo-staging
kubectl -n super-trunfo get deploy,svc,ingress
kubectl -n super-trunfo rollout status deploy/web
kubectl -n super-trunfo rollout status deploy/auth-service
kubectl -n super-trunfo rollout status deploy/card-service
kubectl -n super-trunfo rollout status deploy/matchmaking-service
kubectl -n super-trunfo rollout status deploy/gameplay-service
kubectl -n super-trunfo rollout status deploy/economy-service
kubectl -n super-trunfo rollout status deploy/ranking-service
kubectl -n super-trunfo rollout status deploy/nft-service
kubectl -n super-trunfo rollout status deploy/social-service
kubectl -n super-trunfo rollout status deploy/notification-service
```

Valide endpoints base:

```bash
curl -fsS https://staging.super-trunfo.app/
curl -fsS https://staging.super-trunfo.app/api/auth/health
curl -fsS https://staging.super-trunfo.app/api/cards/health
curl -fsS https://staging.super-trunfo.app/api/matchmaking/health
curl -fsS https://staging.super-trunfo.app/api/match/health
curl -fsS https://staging.super-trunfo.app/api/shop/health
curl -fsS https://staging.super-trunfo.app/api/ranking/health
```

## Smoke Tests

O smoke minimo do RC precisa confirmar:

- Web carrega em staging.
- Cadastro/login retorna token.
- Perfil inicial e deck inicial estao disponiveis.
- Selecao de deck aceita 10 cards validos.
- Matchmaking cria PvE quando nao ha adversario compativel.
- Jogada valida altera estado da partida.
- Resultado atualiza creditos e rating.
- Loja lista ofertas e compra mockada/fixture passa.
- Ranking global reflete resultado.
- Notificacao in-app pode ser enfileirada e listada.

Quando houver credenciais de teste no ambiente, registre o usuario usado e anexe evidencias no PR/release notes.

## Dashboards

Os dashboards do RC sao provisionados pelo manifest `infra/k8s/base/observability.yaml`:

- `Super Trunfo MVP Release Candidate`
- `HTTP 5xx rate`
- `HTTP p95 latency`
- `Matchmaking queue depth`
- `Domain events published`
- `Economy credit balance`

Alertas minimos:

- `SuperTrunfoHighErrorRate`
- `SuperTrunfoSlowApi`
- `SuperTrunfoMatchmakingBacklog`

## Release Decision

Go para beta fechado somente quando:

- CI em `main` esta verde.
- CD para staging concluiu com ArgoCD sincronizado e healthy.
- Smoke tests passaram sem bug critico.
- Dashboards mostram erro 5xx e latencia dentro do limite definido.
- Checklist OWASP MVP esta preenchido.
- Rollback runbook foi revisado para o mesmo SHA/tag.

No-go quando:

- Qualquer bug critico impede login, partida, economia ou ranking.
- Alertas criticos persistem por mais de 10 minutos.
- Secret scan, Trivy, CodeQL ou Sonar falham.
- ArgoCD nao consegue convergir staging.
