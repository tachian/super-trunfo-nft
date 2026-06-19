# Checklist OWASP MVP

Este checklist registra o hardening ST-804 para o release candidate do MVP.

| Controle               | Status                 | Evidencia                                                                 |
| ---------------------- | ---------------------- | ------------------------------------------------------------------------- |
| Rate limit             | Feito                  | Middleware compartilhado por IP, metodo e rota no shared kernel FastAPI.  |
| Validacao server-side  | Feito                  | Pydantic/FastAPI nos contratos e bloqueio de content-type nao JSON.       |
| Limite de payload      | Feito                  | `SUPER_TRUNFO_MAX_REQUEST_BODY_BYTES` bloqueia requests acima do limite.  |
| Logs mascarados LGPD   | Feito                  | `mask_sensitive_data` cobre email, CPF, telefone, celular, nome e tokens. |
| Headers de seguranca   | Feito                  | `nosniff`, `DENY`, `no-referrer`, permissions policy e cache no-store.    |
| HSTS em HTTPS          | Planejado por ambiente | `SUPER_TRUNFO_HSTS_ENABLED=true` em staging/producao HTTPS.               |
| Secret scanning        | Feito                  | Trivy secret scan bloqueante no CI.                                       |
| Vulnerability scanning | Feito                  | CodeQL e Trivy para vulnerabilidades altas/criticas.                      |
| Quality gates          | Feito                  | Ruff, compileall, testes, duplicacao, contratos, lint, build e Sonar.     |
| Revisao de autorizacao | Parcial                | Fluxos autenticados devem evoluir em ST-805 e pos-MVP.                    |
| Runbook de excecoes    | Planejado              | Excecoes de seguranca devem ser aprovadas em ADR/runbook.                 |

## Decisoes

- O rate limit inicial e em memoria por processo. Ele reduz abuso basico no MVP, mas deve migrar para Redis quando houver multiplas replicas por servico.
- Recompensas, notificacoes e ranking continuam validados no backend; clientes nao podem enviar placar, vencedor ou mutacoes de rating.
- HSTS fica configuravel para evitar falso positivo em desenvolvimento local sem HTTPS.
