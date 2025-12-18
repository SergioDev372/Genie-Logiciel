import 'package:flutter/material.dart';

class ForgotPasswordButton extends StatelessWidget {
  final VoidCallback onPressed;

  const ForgotPasswordButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      child: Text(
        'Mot de passe oublié ?',
        style: TextStyle(color: Colors.grey.shade600),
      ),
    );
  }
}
