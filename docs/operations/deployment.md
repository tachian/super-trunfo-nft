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
- lint e compilacao Python;
- testes de cada servico FastAPI;
- build Next.js;
- testes Flutter;
- testes Hardhat;
- build Docker dos servicos;
- CodeQL e Trivy.

O fluxo de CD publica imagens no GitHub Container Registry e aplica as applications ArgoCD para staging ou producao.

## GitOps

Os overlays Kustomize e as applications ArgoCD apontam para `Avalia-Tachian/super-trunfo-nft`.

Secrets esperados no GitHub:

- `KUBE_CONFIG`
- `AWS_ROLE_TO_ASSUME`, quando Terraform/CD usar OIDC para AWS
- senhas de banco e RabbitMQ em um secret manager do ambiente
