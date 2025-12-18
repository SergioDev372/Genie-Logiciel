import 'package:flutter/material.dart';

class QuickActionButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;

  const QuickActionButton({
    super.key,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.blue,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        onPressed: onPressed,
        icon: const Icon(Icons.add),
        label: Text(label),
      ),
    );
  }
}
