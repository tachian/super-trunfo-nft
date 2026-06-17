import 'package:flutter/material.dart';

class PageScaffold extends StatelessWidget {
  const PageScaffold({
    required this.eyebrow,
    required this.title,
    required this.children,
    super.key,
  });

  final String eyebrow;
  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          eyebrow.toUpperCase(),
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Theme.of(context).colorScheme.primary,
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 4),
        Text(title, style: Theme.of(context).textTheme.headlineMedium),
        const SizedBox(height: 16),
        ...children.expand((child) sync* {
          yield child;
          yield const SizedBox(height: 12);
        }),
      ],
    );
  }
}

class MetricValue {
  const MetricValue({
    required this.label,
    required this.value,
  });

  final String label;
  final String value;
}

class MetricRow extends StatelessWidget {
  const MetricRow({
    required this.metrics,
    super.key,
  });

  final List<MetricValue> metrics;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        for (final metric in metrics)
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(right: 8),
              child: MetricCard(
                icon: Icons.insights_rounded,
                label: metric.label,
                value: metric.value,
              ),
            ),
          ),
      ],
    );
  }
}

class MetricCard extends StatelessWidget {
  const MetricCard({
    required this.icon,
    required this.label,
    required this.value,
    super.key,
  });

  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon),
            const SizedBox(height: 8),
            Text(label),
            const SizedBox(height: 4),
            Text(value, style: Theme.of(context).textTheme.titleLarge),
          ],
        ),
      ),
    );
  }
}

class ActionTile extends StatelessWidget {
  const ActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    super.key,
  });

  final IconData icon;
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right_rounded),
      ),
    );
  }
}

class LeaderboardTile extends StatelessWidget {
  const LeaderboardTile({
    required this.position,
    required this.nickname,
    required this.rating,
    super.key,
  });

  final int position;
  final String nickname;
  final int rating;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(child: Text('$position')),
        title: Text(nickname),
        subtitle: const Text('Ranking global'),
        trailing: Text(
          '$rating',
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ),
    );
  }
}
