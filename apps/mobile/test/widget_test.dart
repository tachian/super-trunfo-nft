import 'package:flutter_test/flutter_test.dart';
import 'package:super_trunfo_mobile/src/app.dart';
import 'package:super_trunfo_mobile/src/config/app_environment.dart';

void main() {
  testWidgets('renders mobile shell with login and environment', (
    tester,
  ) async {
    await tester.pumpWidget(
      SuperTrunfoApp(environment: AppEnvironment.testing()),
    );

    expect(find.text('Super Trunfo NFT'), findsOneWidget);
    expect(find.text('Login'), findsWidgets);
    expect(find.text('Local'), findsOneWidget);
    expect(find.text('http://127.0.0.1:8001'), findsOneWidget);
  });

  testWidgets('navigates through MVP routes', (tester) async {
    await tester.pumpWidget(
      SuperTrunfoApp(environment: AppEnvironment.testing()),
    );

    for (final routeLabel in [
      'Colecao',
      'Deck',
      'Partida',
      'Loja',
      'Ranking',
    ]) {
      await tester.tap(find.text(routeLabel).last);
      await tester.pumpAndSettle();

      expect(find.text(routeLabel), findsWidgets);
    }
  });

  test('builds staging environment from overrides', () {
    final environment = AppEnvironment.fromDartDefines(
      environmentName: 'staging',
      apiBaseUrl: 'https://staging.example.test',
    );

    expect(environment.label, 'Staging');
    expect(environment.authBaseUrl.toString(), 'https://staging.example.test');
    expect(
      environment.rankingBaseUrl.toString(),
      'https://staging.example.test',
    );
  });
}
