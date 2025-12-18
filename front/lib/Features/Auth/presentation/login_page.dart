import 'package:flutter/material.dart';

import '../../../view/Auth/widgets/auth_button.dart';
import '../../../view/Auth/widgets/auth_logo.dart';
import '../../../view/Auth/widgets/auth_text_field.dart';
import '../../../view/Auth/widgets/forgot_password_button.dart';


class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool _obscurePassword = true;

  void _onLoginPressed() {
    if (!_formKey.currentState!.validate()) return;

    // logique plus tard
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const AuthLogo(),
                const SizedBox(height: 32),

                /// EMAIL
                AuthTextField(
                  hint: 'Adresse e-mail',
                  icon: Icons.email,
                  controller: emailController,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Veuillez entrer votre e-mail';
                    }
                    final emailRegex =
                    RegExp(r'^[^@]+@[^@]+\.[^@]+');
                    if (!emailRegex.hasMatch(value)) {
                      return 'E-mail invalide';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                /// PASSWORD
                AuthTextField(
                  hint: 'Mot de passe',
                  icon: Icons.lock,
                  controller: passwordController,
                  obscureText: _obscurePassword,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Veuillez entrer votre mot de passe';
                    }
                    if (value.length < 6) {
                      return 'Minimum 6 caractères';
                    }
                    return null;
                  },
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword
                          ? Icons.visibility_off
                          : Icons.visibility,
                    ),
                    onPressed: () {
                      setState(() {
                        _obscurePassword = !_obscurePassword;
                      });
                    },
                  ),
                ),

                const SizedBox(height: 24),

                AuthButton(
                  label: 'Se connecter',
                  onPressed: _onLoginPressed,
                ),

                const SizedBox(height: 16),
                ForgotPasswordButton(onPressed: () {}),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

