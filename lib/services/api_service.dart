import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

class ApiService {
  // URL de producción en Vercel
  static String baseUrl = 'https://snap-card-amlm.vercel.app';

  static const String _tokenKey = 'snapcard_auth_token';
  static const String _userDataKey = 'snapcard_user_data';

  /// Guardar token y datos del usuario en SharedPreferences
  static Future<void> _saveSession(AuthResponse auth) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, auth.accessToken);
    await prefs.setString(_userDataKey, jsonEncode(auth.user.toJson()));
  }

  /// Obtener el token guardado
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  /// Obtener el usuario guardado localmente
  static Future<UserModel?> getSavedUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userJson = prefs.getString(_userDataKey);
    if (userJson == null) return null;
    try {
      return UserModel.fromJson(jsonDecode(userJson) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  /// Cerrar sesión y eliminar token guardado
  static Future<void> logout() async {
    final token = await getToken();
    if (token != null) {
      try {
        await http.post(
          Uri.parse('$baseUrl/auth/logout'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        );
      } catch (_) {}
    }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userDataKey);
  }

  /// Registro de usuario (POST /auth/register)
  static Future<AuthResponse> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name.trim(),
        'email': email.trim().toLowerCase(),
        'password': password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 201) {
      final auth = AuthResponse.fromJson(data as Map<String, dynamic>);
      await _saveSession(auth);
      return auth;
    } else {
      final detail = data is Map && data.containsKey('detail')
          ? data['detail'].toString()
          : 'Error al registrar la cuenta';
      throw ApiException(detail);
    }
  }

  /// Inicio de sesión (POST /auth/login)
  static Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email.trim().toLowerCase(),
        'password': password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      final auth = AuthResponse.fromJson(data as Map<String, dynamic>);
      await _saveSession(auth);
      return auth;
    } else {
      final detail = data is Map && data.containsKey('detail')
          ? data['detail'].toString()
          : 'Correo o contraseña incorrectos';
      throw ApiException(detail);
    }
  }

  /// Obtener perfil del usuario actual (GET /me)
  static Future<UserModel> getProfile() async {
    final token = await getToken();
    if (token == null) {
      throw ApiException('No hay sesión activa');
    }

    final response = await http.get(
      Uri.parse('$baseUrl/me'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final user = UserModel.fromJson(data);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userDataKey, jsonEncode(user.toJson()));
      return user;
    } else {
      throw ApiException('Sesión expirada o no autorizada');
    }
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => message;
}
