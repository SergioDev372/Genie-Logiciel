import 'package:flutter/material.dart';
import '../../../services/auth_api_service.dart';
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

  final _formKey = GlobalKey<FormState>();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  bool _obscurePassword = true;
  bool _isLoading = false;
  String? _errorMessage;

  void _onLoginPressed() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await AuthApiService.login(
        email: emailController.text.trim(),
        password: passwordController.text,
      );

      setState(() {
        _isLoading = false;
      });

      // Gérer les différents cas de réponse
      if (result['statut'] == 'SUCCESS') {
        _showSuccessMessage('Connexion réussie!');
        // TODO: Naviguer vers le tableau de bord
        print('Token JWT: ${result['token']}');
        print('Utilisateur: ${result['utilisateur']}');
      } else if (result['statut'] == 'CHANGEMENT_MOT_DE_PASSE_REQUIS') {
        _showInfoMessage('Vous devez changer votre mot de passe temporaire.');
        // TODO: Naviguer vers la page de changement de mot de passe
        print('Token de changement: ${result['token']}');
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = _getErrorMessage(e);
      });
      
      _showErrorMessage(_errorMessage!);
    }
  }

  String _getErrorMessage(dynamic error) {
    if (error is Map && error.containsKey('detail')) {
      if (error['detail'] is Map) {
        final detail = error['detail'];
        if (detail.containsKey('message')) {
          return detail['message'];
        }
      }
      return error['detail'].toString();
    }
    return 'Erreur de connexion. Veuillez réessayer.';
  }

  void _showSuccessMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showErrorMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );
  }

  void _showInfoMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.blue,
        duration: const Duration(seconds: 3),
      ),
    );
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

                // Message d'erreur
                if (_errorMessage != null)
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      border: Border.all(color: Colors.red.shade200),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.error, color: Colors.red.shade600, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: TextStyle(color: Colors.red.shade600, fontSize: 14),
                          ),
                        ),
                      ],
                    ),
                  ),

                if (_errorMessage != null) const SizedBox(height: 16),

                AuthButton(
                  label: 'Se connecter',
                  onPressed: _onLoginPressed,
                  isLoading: _isLoading,
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

