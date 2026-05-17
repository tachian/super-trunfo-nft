# Services

Cada servico FastAPI representa um contexto de dominio. Todos devem expor:

- `GET /health`
- `GET /ready`
- `GET /context`

Os endpoints de negocio comecam como contratos planejados e ganham implementacao por tarefa.

| Servico | Contexto | Porta |
| --- | --- | --- |
| auth-service | identity | 8001 |
| card-service | cards | 8002 |
| matchmaking-service | matchmaking | 8003 |
| gameplay-service | gameplay | 8004 |
| economy-service | economy | 8005 |
| ranking-service | ranking | 8006 |
| nft-service | nft | 8007 |
| social-service | social | 8008 |
| notification-service | notification | 8009 |

