import 'package:flutter_test/flutter_test.dart';
import 'package:super_trunfo_mobile/main.dart';

void main() {
  testWidgets('renders player dashboard', (tester) async {
    await tester.pumpWidget(const SuperTrunfoApp());

    expect(find.text('Super Trunfo NFT'), findsOneWidget);
    expect(find.text('Rating'), findsOneWidget);
  });
}

