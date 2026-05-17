import 'package:flutter/material.dart';

void main() {
  runApp(const SuperTrunfoApp());
}

class SuperTrunfoApp extends StatelessWidget {
  const SuperTrunfoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Super Trunfo NFT',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF177E89)),
        useMaterial3: true,
      ),
      home: const PlayerDashboardScreen(),
    );
  }
}

class PlayerDashboardScreen extends StatelessWidget {
  const PlayerDashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Super Trunfo NFT')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: const [
          PlayerMetric(label: 'Rating', value: '1480'),
          PlayerMetric(label: 'Creditos', value: '12'),
          PlayerMetric(label: 'Deck', value: '9/10'),
          SizedBox(height: 16),
          FilledButton(onPressed: null, child: Text('Buscar partida')),
        ],
      ),
    );
  }
}

class PlayerMetric extends StatelessWidget {
  const PlayerMetric({required this.label, required this.value, super.key});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(label),
        trailing: Text(value, style: Theme.of(context).textTheme.titleLarge),
      ),
    );
  }
}

