# ADR 0002 - Wallet Custodial

## Status

Aceita

## Contexto

A plataforma evoluira para NFTs reais em Polygon depois da validacao do MVP. O publico principal do jogo nao deve precisar conhecer seed phrase, gas, RPC, bridge ou assinatura on-chain para jogar, comprar cards e participar de ranking. Ao mesmo tempo, a arquitetura precisa preservar a possibilidade de migrar para self-custody quando o jogador quiser assumir controle direto dos ativos.

O contexto NFT ja possui metadados offline, contrato ERC-721 base e feature flag `FEATURE_NFT_ENABLED` desligada por padrao. A wallet custodial deve ser desenhada como capacidade pos-MVP e nao pode bloquear gameplay, economia por creditos ou loja interna.

## Decisao

Adotaremos uma wallet custodial por jogador, provisionada pelo contexto NFT somente quando a feature de blockchain estiver habilitada e houver uma primeira acao on-chain elegivel, como mint, transferencia ou listing em marketplace.

A custodia sera operada pela plataforma com chaves protegidas por servico gerenciado de chaves ou MPC/HSM, nunca persistidas em banco aplicacional, logs, arquivos de configuracao ou variaveis locais de desenvolvimento. O jogador sera dono funcional dos NFTs na experiencia de produto, enquanto a plataforma assina transacoes on-chain em seu nome ate a migracao para wallet externa.

## Onboarding

- Cadastro e login continuam no contexto Identity, sem dependencia de wallet blockchain.
- A wallet custodial sera criada de forma lazy, atras de `FEATURE_NFT_ENABLED`.
- Antes do primeiro uso on-chain, o jogador deve aceitar termos especificos de ativos digitais, custodia e riscos de rede.
- A UI deve exibir status simples: `nao criada`, `custodial ativa`, `congelada`, `migracao solicitada` ou `migrada`.
- O endereco on-chain pode ser exibido ao jogador depois de provisionado, mas private keys e material criptografico nunca sao exportados pela plataforma.
- Falhas de provisionamento nao podem impedir login, colecao off-chain, deck, partida, ranking ou economia por creditos.

## Modelo De Custodia

O contexto NFT sera dono do agregado `CustodialWallet`, com os campos minimos:

- `wallet_id`;
- `player_id`;
- `chain_id`;
- `address`;
- `status`;
- `provider`;
- `created_at`;
- `migrated_to_address`;
- `migrated_at`.

Estados validos:

- `pending`: solicitacao criada, ainda sem endereco confirmado;
- `active`: wallet operacional;
- `frozen`: wallet bloqueada por risco, suporte ou compliance;
- `migration_requested`: jogador iniciou migracao;
- `migrated`: ativos transferidos para wallet externa e custodia encerrada.

Eventos de dominio planejados:

- `CustodialWalletRequested`;
- `CustodialWalletProvisioned`;
- `CustodialWalletFrozen`;
- `CustodialWalletMigrationRequested`;
- `CustodialWalletMigrated`;
- `NFTTransferred`.

## Seguranca

- Chaves privadas devem ficar em KMS, HSM ou MPC gerenciado, com acesso por IAM minimo e segregacao por ambiente.
- Owner de contratos e permissoes administrativas devem usar multisig, nao conta pessoal.
- Servicos de aplicacao nunca recebem private key em texto claro.
- Toda assinatura deve passar por uma politica de autorizacao que valide jogador, wallet, contrato, chain, metodo, valor, nonce e feature flag.
- Transacoes permitidas no inicio ficam restritas a contratos internos conhecidos e metodos explicitamente allowlisted.
- Mints, transfers e listings devem ter idempotency key e trilha de auditoria.
- Logs devem mascarar identificadores sensiveis quando combinados com dados pessoais e nunca registrar payloads de assinatura, segredos, tokens ou material criptografico.
- Operacoes administrativas exigem MFA, auditoria e aprovacao fora de banda para acoes de alto risco.
- Rate limit e deteccao de abuso devem ser aplicados a mint, transfer, listing e migracao.
- Incidentes podem colocar wallets em `frozen`, bloqueando novas assinaturas ate revisao.

## Limites De Dominio

- Identity autentica o jogador, mantem consentimentos e fornece `player_id`.
- NFT gerencia wallet custodial, metadados, mint requests e ownership on-chain.
- Economy continua responsavel por creditos internos, compras e telemetria economica.
- Marketplace usara a wallet custodial para listar e transferir NFTs quando a feature estiver habilitada.
- Notification comunica provisionamento, migracao, congelamento e transferencias relevantes.
- Observability registra metricas de provisionamento, falhas de assinatura, tempo de confirmacao e migracoes.

## Migracao Futura Para Self-Custody

A migracao nao exportara a private key custodial. O jogador conectara uma wallet externa e assinara um desafio para provar controle do endereco de destino. Depois disso, o contexto NFT criara uma solicitacao de migracao e transferira os NFTs da wallet custodial para a wallet externa usando `safeTransferFrom`.

Fluxo planejado:

1. Jogador solicita migracao na UI.
2. UI conecta wallet externa e solicita assinatura de desafio com nonce curto.
3. Backend valida assinatura, chain e endereco.
4. Wallet entra em `migration_requested`.
5. Servico de custodia assina transferencias para o endereco externo.
6. Eventos `NFTTransferred` sao publicados para cada ativo.
7. Wallet entra em `migrated` e novas operacoes custodiais sao bloqueadas.

Depois da migracao, o jogador passa a assumir gas, seguranca da wallet externa e eventuais perdas por autocustodia. A plataforma pode continuar exibindo os ativos por leitura on-chain, mas nao assina novas transacoes pelo jogador.

## Decisoes Adiadas

- Provedor final de custodia, KMS ou MPC.
- Uso de account abstraction ou EOA custodial por jogador.
- Rede inicial exata, embora Polygon seja a direcao de produto.
- Politica comercial de gas sponsorship.
- Processo juridico final para termos, suporte, congelamento e compliance.

## Consequencias

- O onboarding continua simples para jogadores nao cripto.
- Blockchain permanece opcional e atras de feature flag, preservando o foco do MVP.
- A plataforma assume responsabilidade operacional e de seguranca sobre custodia enquanto a wallet estiver ativa.
- O desenho permite migracao para self-custody sem expor private keys.
- Sera necessario hardening adicional antes de producao: threat model, runbook de incidentes, auditoria de contrato, monitoramento on-chain e revisao juridica.
