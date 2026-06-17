import 'package:flutter/material.dart';

import '../config/app_environment.dart';
import '../widgets/card_visual.dart';
import '../widgets/page_scaffold.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({
    required this.environment,
    super.key,
  });

  static const routePath = '/login';

  final AppEnvironment environment;

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      eyebrow: 'Acesso MVP',
      title: 'Login',
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const TextField(
                  decoration: InputDecoration(labelText: 'Email'),
                  keyboardType: TextInputType.emailAddress,
                ),
                const SizedBox(height: 12),
                const TextField(
                  decoration: InputDecoration(labelText: 'Senha'),
                  obscureText: true,
                ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.login_rounded),
                  label: const Text('Entrar'),
                ),
              ],
            ),
          ),
        ),
        MetricCard(
          icon: Icons.cloud_queue_rounded,
          label: 'Auth service',
          value: environment.authBaseUrl.toString(),
        ),
      ],
    );
  }
}

class CollectionScreen extends StatelessWidget {
  const CollectionScreen({super.key});

  static const routePath = '/colecao';

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      eyebrow: 'Cards',
      title: 'Colecao',
      children: [
        const MetricRow(
          metrics: [
            MetricValue(label: 'Total', value: '4'),
            MetricValue(label: 'Familias', value: '4'),
            MetricValue(label: 'Raridade', value: 'Lendario'),
          ],
        ),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: const [
            CardVisual(
              name: 'Aurora Runner',
              family: 'Solar',
              rarity: 'Raro',
              level: 84,
            ),
            CardVisual(
              name: 'Granite Guard',
              family: 'Terra',
              rarity: 'Epico',
              level: 88,
            ),
            CardVisual(
              name: 'Pulse Scholar',
              family: 'Arcano',
              rarity: 'Lendario',
              level: 95,
            ),
          ],
        ),
      ],
    );
  }
}

class DeckScreen extends StatelessWidget {
  const DeckScreen({super.key});

  static const routePath = '/deck';

  @override
  Widget build(BuildContext context) {
    return const PageScaffold(
      eyebrow: 'Deck ativo',
      title: 'Deck',
      children: [
        MetricRow(
          metrics: [
            MetricValue(label: 'Selecionadas', value: '3/10'),
            MetricValue(label: 'Nivel medio', value: '89'),
            MetricValue(label: 'Tolerancia', value: '+/-20'),
          ],
        ),
        ActionTile(
          icon: Icons.layers_rounded,
          title: 'Salvar deck',
          subtitle: 'Cartas prontas para matchmaking',
        ),
        ActionTile(
          icon: Icons.rule_rounded,
          title: 'Validacao',
          subtitle: 'Deck minimo ainda pendente',
        ),
      ],
    );
  }
}

class MatchScreen extends StatelessWidget {
  const MatchScreen({super.key});

  static const routePath = '/partida';

  @override
  Widget build(BuildContext context) {
    return const PageScaffold(
      eyebrow: 'Mesa MVP',
      title: 'Partida',
      children: [
        CardVisual(
          name: 'Pulse Scholar',
          family: 'Arcano',
          rarity: 'Lendario',
          level: 95,
        ),
        MetricRow(
          metrics: [
            MetricValue(label: 'Rodada', value: '1/10'),
            MetricValue(label: 'Jogador', value: '0'),
            MetricValue(label: 'Oponente', value: '0'),
          ],
        ),
        ActionTile(
          icon: Icons.play_arrow_rounded,
          title: 'Buscar partida',
          subtitle: 'Fila por nivel medio do deck',
        ),
      ],
    );
  }
}

class ShopScreen extends StatelessWidget {
  const ShopScreen({super.key});

  static const routePath = '/loja';

  @override
  Widget build(BuildContext context) {
    return const PageScaffold(
      eyebrow: 'Economia',
      title: 'Loja',
      children: [
        MetricRow(
          metrics: [
            MetricValue(label: 'Saldo', value: '128'),
            MetricValue(label: 'Ofertas', value: '3'),
            MetricValue(label: 'Inventario', value: '4'),
          ],
        ),
        ActionTile(
          icon: Icons.shopping_cart_rounded,
          title: 'Pack raro',
          subtitle: '45 creditos',
        ),
        ActionTile(
          icon: Icons.autorenew_rounded,
          title: 'Renovacao epica',
          subtitle: '30 creditos',
        ),
      ],
    );
  }
}

class RankingScreen extends StatelessWidget {
  const RankingScreen({super.key});

  static const routePath = '/ranking';

  @override
  Widget build(BuildContext context) {
    return const PageScaffold(
      eyebrow: 'Temporada atual',
      title: 'Ranking',
      children: [
        LeaderboardTile(position: 1, nickname: 'TachiMaster', rating: 1842),
        LeaderboardTile(position: 2, nickname: 'DeckForge', rating: 1710),
        LeaderboardTile(position: 3, nickname: 'CardPilot', rating: 1596),
      ],
    );
  }
}
