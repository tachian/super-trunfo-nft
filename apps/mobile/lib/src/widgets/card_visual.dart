import 'package:flutter/material.dart';

class CardVisual extends StatelessWidget {
  const CardVisual({
    required this.name,
    required this.family,
    required this.rarity,
    required this.level,
    super.key,
  });

  final String name;
  final String family;
  final String rarity;
  final int level;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return SizedBox(
      width: 220,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                height: 112,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: colorScheme.outlineVariant),
                  gradient: LinearGradient(
                    colors: [
                      colorScheme.primaryContainer,
                      colorScheme.tertiaryContainer,
                    ],
                  ),
                ),
                child: Center(
                  child: Icon(
                    Icons.auto_awesome_rounded,
                    color: colorScheme.onPrimaryContainer,
                    size: 36,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text(name, style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 4),
              Text('$family - $rarity'),
              const SizedBox(height: 8),
              Text('Nivel $level'),
            ],
          ),
        ),
      ),
    );
  }
}
