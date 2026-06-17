import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../config/app_environment.dart';
import 'screens.dart';

class MobileShell extends StatelessWidget {
  const MobileShell({
    required this.currentPath,
    required this.environment,
    required this.child,
    super.key,
  });

  final String currentPath;
  final AppEnvironment environment;
  final Widget child;

  static const _destinations = [
    _ShellDestination(
      label: 'Login',
      icon: Icons.login_rounded,
      path: LoginScreen.routePath,
    ),
    _ShellDestination(
      label: 'Colecao',
      icon: Icons.auto_stories_rounded,
      path: CollectionScreen.routePath,
    ),
    _ShellDestination(
      label: 'Deck',
      icon: Icons.layers_rounded,
      path: DeckScreen.routePath,
    ),
    _ShellDestination(
      label: 'Partida',
      icon: Icons.play_arrow_rounded,
      path: MatchScreen.routePath,
    ),
    _ShellDestination(
      label: 'Loja',
      icon: Icons.storefront_rounded,
      path: ShopScreen.routePath,
    ),
    _ShellDestination(
      label: 'Ranking',
      icon: Icons.emoji_events_rounded,
      path: RankingScreen.routePath,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final selectedIndex = _destinations.indexWhere(
      (destination) => destination.path == currentPath,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Super Trunfo NFT'),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Chip(
              label: Text(environment.label),
              visualDensity: VisualDensity.compact,
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: child,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: selectedIndex < 0 ? 0 : selectedIndex,
        onDestinationSelected: (index) {
          context.go(_destinations[index].path);
        },
        destinations: [
          for (final destination in _destinations)
            NavigationDestination(
              icon: Icon(destination.icon),
              label: destination.label,
            ),
        ],
      ),
    );
  }
}

class _ShellDestination {
  const _ShellDestination({
    required this.label,
    required this.icon,
    required this.path,
  });

  final String label;
  final IconData icon;
  final String path;
}
