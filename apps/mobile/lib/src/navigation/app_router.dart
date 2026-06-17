import 'package:go_router/go_router.dart';

import '../config/app_environment.dart';
import '../presentation/mobile_shell.dart';
import '../presentation/screens.dart';

GoRouter createAppRouter(AppEnvironment environment) {
  return GoRouter(
    initialLocation: LoginScreen.routePath,
    routes: [
      ShellRoute(
        builder: (context, state, child) {
          return MobileShell(
            currentPath: state.uri.path,
            environment: environment,
            child: child,
          );
        },
        routes: [
          GoRoute(
            path: LoginScreen.routePath,
            builder: (context, state) {
              return LoginScreen(environment: environment);
            },
          ),
          GoRoute(
            path: CollectionScreen.routePath,
            builder: (context, state) {
              return const CollectionScreen();
            },
          ),
          GoRoute(
            path: DeckScreen.routePath,
            builder: (context, state) {
              return const DeckScreen();
            },
          ),
          GoRoute(
            path: MatchScreen.routePath,
            builder: (context, state) {
              return const MatchScreen();
            },
          ),
          GoRoute(
            path: ShopScreen.routePath,
            builder: (context, state) {
              return const ShopScreen();
            },
          ),
          GoRoute(
            path: RankingScreen.routePath,
            builder: (context, state) {
              return const RankingScreen();
            },
          ),
        ],
      ),
    ],
  );
}
