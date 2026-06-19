# Rastreabilidade de Requisitos

Este documento conecta os principais requisitos do PDF as entregas planejadas.

| Requisito do PDF                    | Entrega no projeto                                  | Tarefas                                |
| ----------------------------------- | --------------------------------------------------- | -------------------------------------- |
| Plataforma web, Android e iOS       | Next.js web e Flutter mobile                        | ST-601, ST-602, ST-603, ST-604, ST-605 |
| Backend Python/FastAPI              | Servicos FastAPI por contexto                       | ST-003, ST-101, ST-201, ST-302, ST-501 |
| DDD + arquitetura hexagonal         | Contextos e shared kernel                           | ST-003                                 |
| SOLID e estrutura uniforme          | Padroes de engenharia dos servicos                  | ST-003, ST-004                         |
| Logs estruturados e LGPD            | Observability layer, correlation id e mascaramento  | ST-003, ST-804                         |
| Identity Context                    | Auth, perfil e social base                          | ST-101, ST-102, ST-105, ST-801         |
| Card Context                        | Cards, NFT metadata, expiracao e colecao            | ST-201, ST-202, ST-203, ST-204, ST-205 |
| Match/Game Context                  | Match, round, gameplay e BOT                        | ST-301, ST-302, ST-303, ST-304, ST-305 |
| Economy Context                     | Creditos, loja e inventario                         | ST-501, ST-502, ST-505                 |
| Ranking Context                     | ELO/MMR, tiers e rankings                           | ST-503, ST-504                         |
| Notification Context                | Push e alertas                                      | ST-802                                 |
| Matchmaking por nivel medio do deck | Redis queue e tolerancia +/-20                      | ST-401, ST-402, ST-403                 |
| Cards nunca identicos               | Hash SHA-256 e regeneracao                          | ST-202                                 |
| Expiracao de cards                  | Formula de validade                                 | ST-203                                 |
| Geração procedural                  | Worker periodico                                    | ST-204                                 |
| NFT Polygon ERC-721                 | Smart contract e metadados                          | ST-701, ST-705                         |
| Marketplace e negociacao            | Listing, trades e eventos                           | ST-703, ST-704                         |
| Anti-cheat                          | Backend autoritativo, replay auditavel e validacoes | ST-304, ST-404                         |
| DevOps GitHub Actions               | CI/CD, Docker, scan, staging/producao               | ST-004, ST-005, ST-804, ST-805         |
| Qualidade bloqueante no CI          | Lint, PEP8/Ruff, duplicacao, CodeQL/Trivy e Sonar   | ST-004, ST-804                         |
| Observabilidade                     | Prometheus, Grafana, Loki, OpenTelemetry e Jaeger   | ST-004, ST-804, ST-805                 |
| Escalabilidade AWS                  | Terraform, EKS, RDS, Redis, S3 e CloudFront         | ST-004, ST-805                         |
