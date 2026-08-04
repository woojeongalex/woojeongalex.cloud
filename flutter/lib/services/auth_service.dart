import 'dart:convert';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:kakao_flutter_sdk_user/kakao_flutter_sdk_user.dart';

class AuthService {
  static const String _authBaseUrl = 'https://auth.woojeongalex.cloud';
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';

  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  String? lastError;

  Future<bool> isLoggedIn() async {
    final token = await _storage.read(key: _keyAccessToken);
    return token != null;
  }

  Future<bool> loginWithKakao() async {
    lastError = null;
    final String kakaoAccessToken;
    try {
      kakaoAccessToken = await _getKakaoToken();
    } catch (e) {
      lastError = 'Kakao: $e';
      return false;
    }

    try {
      final response = await http.post(
        Uri.parse('$_authBaseUrl/auth/kakao/mobile'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'access_token': kakaoAccessToken}),
      );

      if (response.statusCode != 200) {
        lastError = 'Backend ${response.statusCode}: ${response.body}';
        return false;
      }

      final body = jsonDecode(response.body) as Map<String, dynamic>;
      await _storage.write(
        key: _keyAccessToken,
        value: body['access_token'] as String,
      );
      await _storage.write(
        key: _keyRefreshToken,
        value: body['refresh_token'] as String,
      );
      return true;
    } catch (e) {
      lastError = 'Backend: $e';
      return false;
    }
  }

  Future<void> logout() async {
    await _storage.delete(key: _keyAccessToken);
    await _storage.delete(key: _keyRefreshToken);
  }

  Future<String?> getAccessToken() => _storage.read(key: _keyAccessToken);

  Future<String> _getKakaoToken() async {
    OAuthToken token;
    if (await isKakaoTalkInstalled()) {
      token = await UserApi.instance.loginWithKakaoTalk();
    } else {
      token = await UserApi.instance.loginWithKakaoAccount();
    }
    return token.accessToken;
  }
}
