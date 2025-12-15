import 'package:flutter/material.dart';
import '../widgets/auth_button.dart';
import '../widgets/auth_logo.dart';
import '../widgets/auth_text_field.dart';
import '../widgets/forgot_password_button.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const AuthLogo(),
              const SizedBox(height: 32),

              AuthTextField(
                hint: 'Adresse e-mail',
                icon: Icons.email,
                controller: emailController,
              ),
              const SizedBox(height: 16),

              AuthTextField(
                hint: 'Mot de passe',
                icon: Icons.lock,
                controller: passwordController,
                obscureText: true,
              ),
              const SizedBox(height: 24),

              AuthButton(
                label: 'Se connecter',
                onPressed: () {
                  // logique plus tard
                },
              ),
              const SizedBox(height: 16),

              ForgotPasswordButton(
                onPressed: () {
                  // navigation plus tard
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
