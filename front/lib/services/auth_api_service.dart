import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthApiService {
  static const String baseUrl = 'http://localhost:8000';

  static Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode({
        'email': email,
        'mot_de_passe': password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode >= 400) {
      throw data;
    }

    return data;
  }
}
