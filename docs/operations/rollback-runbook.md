# Rollback Runbook

Este runbook descreve rollback do release candidate ST-805 em staging e producao.

## Rollback Triggers

Acione rollback quando ocorrer qualquer item abaixo:

- Erro 5xx persistente acima do limite do alerta `SuperTrunfoHighErrorRate`.
- Login, deck, partida, economia ou ranking indisponiveis.
- ArgoCD em estado `Degraded` ou `OutOfSync` sem convergir.
- Deploy introduz falha de seguranca, secret exposto ou regressao de autorizacao.
- Latencia p95 acima de um segundo por mais de 10 minutos em fluxo critico.

## GitOps Rollback

Para voltar o staging ao commit anterior:

```bash
git revert <sha-do-release-candidate>
git push origin main
gh workflow run CD --ref main -f environment=staging
```

Depois acompanhe:

```bash
kubectl -n argocd get application super-trunfo-staging
kubectl -n super-trunfo get pods
kubectl -n super-trunfo rollout status deploy/web
```

Para producao, use a tag estavel anterior e atualize o overlay `production` para a imagem/tag aprovada antes de disparar:

```bash
gh workflow run CD --ref stable -f environment=production
```

## Image Rollback

Se o GitOps ainda nao convergiu e a mitigacao precisa ser imediata, use rollback de deployment:

```bash
kubectl -n super-trunfo rollout undo deploy/web
kubectl -n super-trunfo rollout undo deploy/auth-service
kubectl -n super-trunfo rollout undo deploy/card-service
kubectl -n super-trunfo rollout undo deploy/matchmaking-service
kubectl -n super-trunfo rollout undo deploy/gameplay-service
kubectl -n super-trunfo rollout undo deploy/economy-service
kubectl -n super-trunfo rollout undo deploy/ranking-service
kubectl -n super-trunfo rollout undo deploy/nft-service
kubectl -n super-trunfo rollout undo deploy/social-service
kubectl -n super-trunfo rollout undo deploy/notification-service
```

Em seguida, sincronize o GitOps com o estado desejado para evitar drift permanente.

## Data Safety

- Nao execute rollback destrutivo de banco sem backup validado.
- Preserve eventos RabbitMQ e dados transacionais para auditoria.
- Se a falha envolver economia/ranking, congele novos deploys e exporte saldos/rating antes de reparos.
- Para schema breaking change, crie hotfix forward-compatible antes de reverter aplicacao.

## Post-Rollback

Depois da estabilizacao:

- Registre o incidente no backlog com SHA, ambiente, horario e impacto.
- Anexe graficos do dashboard do RC.
- Documente se houve perda de dados, reprocessamento de eventos ou ajuste manual.
- Reabra o release candidate somente apos CI, smoke e dashboards voltarem ao normal.
