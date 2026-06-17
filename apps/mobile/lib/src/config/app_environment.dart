enum AppEnvironmentName {
  local,
  staging,
  production,
}

class AppEnvironment {
  const AppEnvironment({
    required this.name,
    required this.apiBaseUrl,
    required this.authBaseUrl,
    required this.cardsBaseUrl,
    required this.matchmakingBaseUrl,
    required this.gameplayBaseUrl,
    required this.economyBaseUrl,
    required this.rankingBaseUrl,
  });

  final AppEnvironmentName name;
  final Uri apiBaseUrl;
  final Uri authBaseUrl;
  final Uri cardsBaseUrl;
  final Uri matchmakingBaseUrl;
  final Uri gameplayBaseUrl;
  final Uri economyBaseUrl;
  final Uri rankingBaseUrl;

  String get label {
    return switch (name) {
      AppEnvironmentName.local => 'Local',
      AppEnvironmentName.staging => 'Staging',
      AppEnvironmentName.production => 'Production',
    };
  }

  factory AppEnvironment.fromDartDefines({
    String environmentName = const String.fromEnvironment(
      'SUPER_TRUNFO_ENV',
      defaultValue: 'local',
    ),
    String apiBaseUrl = const String.fromEnvironment(
      'SUPER_TRUNFO_API_BASE_URL',
      defaultValue: '',
    ),
  }) {
    final name = _parseName(environmentName);
    final baseUrl = apiBaseUrl.trim().isEmpty
        ? _defaultBaseUrl(name)
        : Uri.parse(apiBaseUrl.trim());

    return AppEnvironment.fromBaseUrl(name: name, apiBaseUrl: baseUrl);
  }

  factory AppEnvironment.fromBaseUrl({
    required AppEnvironmentName name,
    required Uri apiBaseUrl,
  }) {
    _validateBaseUrl(name, apiBaseUrl);

    return AppEnvironment(
      name: name,
      apiBaseUrl: apiBaseUrl,
      authBaseUrl: _serviceBaseUrl(name, apiBaseUrl, 8001),
      cardsBaseUrl: _serviceBaseUrl(name, apiBaseUrl, 8002),
      matchmakingBaseUrl: _serviceBaseUrl(name, apiBaseUrl, 8003),
      gameplayBaseUrl: _serviceBaseUrl(name, apiBaseUrl, 8004),
      economyBaseUrl: _serviceBaseUrl(name, apiBaseUrl, 8005),
      rankingBaseUrl: _serviceBaseUrl(name, apiBaseUrl, 8006),
    );
  }

  static AppEnvironment testing() {
    return AppEnvironment.fromBaseUrl(
      name: AppEnvironmentName.local,
      apiBaseUrl: Uri.https('127.0.0.1:8001'),
    );
  }
}

AppEnvironmentName _parseName(String value) {
  return switch (value.trim().toLowerCase()) {
    'staging' => AppEnvironmentName.staging,
    'production' || 'prod' => AppEnvironmentName.production,
    _ => AppEnvironmentName.local,
  };
}

Uri _defaultBaseUrl(AppEnvironmentName name) {
  return switch (name) {
    AppEnvironmentName.local => Uri.https('localhost:8001'),
    AppEnvironmentName.staging => Uri.parse('https://staging.super-trunfo.app'),
    AppEnvironmentName.production => Uri.parse('https://super-trunfo.app'),
  };
}

void _validateBaseUrl(AppEnvironmentName name, Uri apiBaseUrl) {
  if (name == AppEnvironmentName.local) {
    return;
  }

  if (apiBaseUrl.scheme != 'https') {
    throw ArgumentError.value(
      apiBaseUrl.toString(),
      'apiBaseUrl',
      'Remote mobile environments require HTTPS.',
    );
  }
}

Uri _serviceBaseUrl(AppEnvironmentName name, Uri apiBaseUrl, int localPort) {
  return switch (name) {
    AppEnvironmentName.local => apiBaseUrl.replace(port: localPort),
    AppEnvironmentName.staging => apiBaseUrl,
    AppEnvironmentName.production => apiBaseUrl,
  };
}
