# Deployment

## Local

```bash
docker compose -f infra/docker/compose.yaml up --build
```

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

O fluxo de CD publica imagens no GitHub Container Registry em pushes para `main` e tags `v*.*.*`.

O deploy GitOps e controlado manualmente por `workflow_dispatch`, escolhendo `staging` ou `production`. Isso evita tentativas automaticas de deploy sem `KUBE_CONFIG` ou sem aprovacao do ambiente.

## GitOps

Os overlays Kustomize e as applications ArgoCD apontam para `tachian/super-trunfo-nft`.

Secrets esperados no GitHub:

- `KUBE_CONFIG`
- `AWS_ROLE_TO_ASSUME`, quando Terraform/CD usar OIDC para AWS
- senhas de banco e RabbitMQ em um secret manager do ambiente
