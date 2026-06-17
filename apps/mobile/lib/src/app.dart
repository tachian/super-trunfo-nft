import 'package:flutter/material.dart';

import 'config/app_environment.dart';
import 'navigation/app_router.dart';
import 'theme/app_theme.dart';

class SuperTrunfoApp extends StatelessWidget {
  const SuperTrunfoApp({
    required this.environment,
    super.key,
  });

  final AppEnvironment environment;

  @override
  Widget build(BuildContext context) {
    final router = createAppRouter(environment);

    return MaterialApp.router(
      title: 'Super Trunfo NFT',
      theme: buildAppTheme(),
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
