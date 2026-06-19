# Deployment

## Local

```bash
docker compose -f infra/docker/compose.yaml up --build
```

Guia completo: `docs/operations/local-development.md`.

Servicos locais:

- Web: `http://localhost:3000`
- Auth: `http://localhost:8001/health`
- Cards: `http://localhost:8002/health`
- Matchmaking: `http://localhost:8003/health`
- Gameplay: `http://localhost:8004/health`

## CI/CD

O fluxo de CI executa:

- contratos OpenAPI/eventos;
- lint, type check e PEP8/Ruff;
- checagem de duplicacao com `pnpm quality:duplicates`;
- testes de cada servico FastAPI;
- build Next.js;
- testes Flutter;
- testes Hardhat;
- build Docker dos servicos;
- CodeQL e Trivy bloqueando vulnerabilidades altas ou criticas.

Quando `SONAR_ENABLED=true` e `SONAR_TOKEN` estiver configurado no GitHub, o CI tambem executa SonarCloud com quality gate bloqueante.

## Hardening de Servicos

Os servicos FastAPI herdam hardening do shared kernel. Para staging e producao, configure:

| Variavel                                 | Valor sugerido            | Observacao                                       |
| ---------------------------------------- | ------------------------- | ------------------------------------------------ |
| `SUPER_TRUNFO_RATE_LIMIT_ENABLED`        | `true`                    | Mantem rate limit ativo.                         |
| `SUPER_TRUNFO_RATE_LIMIT_REQUESTS`       | `120`                     | Ajustar por endpoint quando houver telemetria.   |
| `SUPER_TRUNFO_RATE_LIMIT_WINDOW_SECONDS` | `60`                      | Janela padrao de um minuto.                      |
| `SUPER_TRUNFO_RATE_LIMIT_EXCLUDED_PATHS` | `/health,/ready,/context` | Exclusao apenas para probes sem dados sensiveis. |
| `SUPER_TRUNFO_MAX_REQUEST_BODY_BYTES`    | `1048576`                 | 1 MiB por request no MVP.                        |
| `SUPER_TRUNFO_HSTS_ENABLED`              | `true`                    | Usar somente atras de HTTPS valido.              |

O CI bloqueia vulnerabilidades altas/criticas e secrets detectados por Trivy. Excecoes devem ser registradas em ADR ou runbook antes de qualquer merge.

O fluxo de CD publica imagens no GitHub Container Registry em pushes para `main` e tags `v*.*.*`.

O deploy GitOps e controlado manualmente por `workflow_dispatch`, escolhendo `staging` ou `production`. Isso evita tentativas automaticas de deploy sem `KUBE_CONFIG` ou sem aprovacao do ambiente.

## GitOps

Os overlays Kustomize e as applications ArgoCD apontam para `tachian/super-trunfo-nft`.

Secrets esperados no GitHub:

- `KUBE_CONFIG`
- `AWS_ROLE_TO_ASSUME`, quando Terraform/CD usar OIDC para AWS
- senhas de banco e RabbitMQ em um secret manager do ambiente

## Release Candidate

Antes de acionar staging, rode:

```bash
pnpm release:check
```

O runbook completo fica em `docs/operations/release-candidate.md` e o procedimento de rollback fica em `docs/operations/rollback-runbook.md`.

O ST-805 exige:

- ArgoCD staging apontando para `main` e overlay `infra/k8s/overlays/staging`;
- dashboards e alertas do RC em `infra/k8s/base/observability.yaml`;
- smoke tests manuais/automatizados registrados no release;
- rollback testado ou revisado para o SHA/tag do release candidate.
