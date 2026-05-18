# Backlog

## Epicos

| ID    | Epico                  | Objetivo                                                             | Fase     |
| ----- | ---------------------- | -------------------------------------------------------------------- | -------- |
| EP-01 | Fundacao de Plataforma | Monorepo, CI/CD, padroes, ambiente local e observabilidade inicial.  | Fundacao |
| EP-02 | Identity & Social Base | Usuarios, login, perfil, amigos e convites.                          | MVP      |
| EP-03 | Cards & Colecao        | Cards unicos, geracao procedural, expiracao, raridade e colecao.     | MVP      |
| EP-04 | Gameplay & Match       | Regras de partida, rodadas, BOT, PvP/PvE e validacoes anti-cheat.    | MVP      |
| EP-05 | Matchmaking            | Filas, pareamento por nivel medio do deck e fallback para BOT.       | MVP      |
| EP-06 | Economy & Shop         | Creditos, loja, compras, renovacao, packs e inventario.              | MVP      |
| EP-07 | Ranking & Seasons      | ELO/MMR, tiers, ranking global/friends e temporadas.                 | MVP      |
| EP-08 | Web & Mobile Apps      | Experiencia Next.js e Flutter para jogar e gerenciar colecao.        | MVP      |
| EP-09 | NFT & Blockchain       | ERC-721, metadados, Polygon, wallet custodial e eventos on-chain.    | Pos-MVP  |
| EP-10 | Marketplace & Trades   | Listagem, ofertas, escrow, leiloes, reputacao e historico de precos. | Pos-MVP  |
| EP-11 | Notifications          | Push, alertas, convites, eventos e mensagens de sistema.             | Escala   |
| EP-12 | Analytics & Anti-Fraud | Telemetria, balanceamento, anti-cheat e deteccao de abuso economico. | Escala   |

## Definition of Ready

- Historia ligada a um epico e a uma sprint.
- Criterios de aceite escritos.
- Dependencias tecnicas mapeadas.
- Eventos de dominio e APIs descritos quando aplicavel.
- Impacto em seguranca, observabilidade e testes avaliado.

## Definition of Done

- Codigo ou documentacao revisados localmente.
- Testes relevantes adicionados ou atualizados.
- Healthcheck e logs estruturados quando houver servico.
- Docker/CI atualizado quando a tarefa alterar build ou runtime.
- Commit com o ID da tarefa.
- Push para GitHub ao final da tarefa.
