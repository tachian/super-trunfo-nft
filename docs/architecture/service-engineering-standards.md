# Padroes de Engenharia dos Servicos

Este documento registra premissas obrigatorias para todo codigo backend gerado no projeto. Quando uma historia criar ou alterar um servico, estes padroes fazem parte do contexto de aceite.

## DDD e Estrutura Padrao

Todos os servicos devem continuar organizados por contexto delimitado e arquitetura hexagonal. A estrutura alvo para cada servico FastAPI e:

```text
apps/services/<service-name>/
  src/app/
    api/
    application/
    domain/
    infrastructure/
    observability/
    main.py
  tests/
```

- `domain`: entidades, value objects, agregados, eventos e regras puras do dominio.
- `application`: casos de uso, comandos, queries, portas e orquestracao transacional.
- `infrastructure`: adapters de banco, cache, mensageria, clients HTTP, provedores externos e repositorios concretos.
- `api`: rotas FastAPI, schemas, autenticacao/autorizacao e traducao HTTP.
- `observability`: configuracao de logs, correlation id, metricas e traces especificos do servico.

Nenhum servico deve acessar tabelas, modelos internos ou codigo privado de outro contexto. Integracoes entre contextos devem acontecer por contratos REST/eventos publicados em `packages/api-contracts` ou por portas/adapters declarados no proprio servico.

## SOLID

O desenho de codigo deve seguir SOLID:

- Single Responsibility: rotas apenas traduzem HTTP, casos de uso orquestram, dominio decide regras e adapters lidam com I/O.
- Open/Closed: novas estrategias, politicas e provedores devem entrar por interfaces/ports sem alterar regras centrais ja testadas.
- Liskov Substitution: implementacoes de repositorios, mensageria e clients externos precisam preservar o contrato das portas.
- Interface Segregation: portas pequenas e especificas por caso de uso, evitando interfaces genericas de servico.
- Dependency Inversion: application/domain dependem de abstracoes; infrastructure implementa essas abstracoes.

## Logs Estruturados e LGPD

Todos os servicos backend devem emitir logs estruturados em JSON com, no minimo, `timestamp`, `level`, `service`, `context`, `correlation_id`, `event`, `method` e `path` quando houver request HTTP.

Eventos obrigatorios de log:

- Entrada de request externa: registrar metodo, rota, parametros, query string e body de entrada ja mascarado.
- Saida de request externa: registrar o metodo/caso de uso que esta respondendo, status code e payload de resposta ja mascarado.
- Integracao com servico externo ou outro contexto: antes do request, registrar destino, metodo, rota, headers permitidos e payload mascarado.
- Resultado de integracao: registrar status, tempo de resposta, identificador de correlacao remoto quando houver e payload/erro mascarado.

Campos sensiveis devem ser mascarados antes de irem para logs, traces ou labels de metricas. A mascara e obrigatoria para chaves contendo `name`, `nome`, `full_name`, `telefone`, `phone`, `celular`, `cpf`, `email`, `password`, `senha`, `token`, `secret`, `authorization` e equivalentes.

Regras minimas de mascara:

- Email: manter apenas primeira letra e dominio, exemplo `t***@example.com`.
- CPF: manter apenas dois ultimos digitos, exemplo `***.***.***-12`.
- Telefone: manter apenas dois ultimos digitos, exemplo `*********12`.
- Nome: manter apenas primeira letra de cada parte, exemplo `T*** S***`.
- Tokens, senhas e secrets: substituir por `[REDACTED]`.

Falhas devem registrar erro, codigo e stack trace somente quando nao expuserem dados pessoais, credenciais, payload completo ou tokens.

## Qualidade e Gates de CI

O CI deve falhar quando qualquer gate obrigatorio encontrar problema:

- Formatacao: Prettier para workspace Node/TypeScript/docs.
- Lint e type check: TypeScript/Next.js, Hardhat/Solidity e regras locais por pacote.
- PEP8/Python: Ruff para estilo e erros estaticos; `compileall` para sintaxe.
- Testes: unitarios, integracao e smoke tests relevantes por servico/app.
- Duplicacao: `pnpm quality:duplicates` bloqueia blocos duplicados em codigo de producao.
- Vulnerabilidades: CodeQL e Trivy bloqueiam achados de severidade alta ou critica.
- Contratos: OpenAPI/eventos em `packages/api-contracts` precisam validar antes do merge.

SonarCloud deve ser usado quando o repositorio estiver configurado com `SONAR_TOKEN` e variavel `SONAR_ENABLED=true`. Quando habilitado, o quality gate SonarCloud e bloqueante por `sonar.qualitygate.wait=true`.
