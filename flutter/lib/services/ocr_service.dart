import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

class OcrResult {
  final String url;
  final String key;
  final String text;

  OcrResult({required this.url, required this.key, required this.text});

  factory OcrResult.fromJson(Map<String, dynamic> json) {
    return OcrResult(
      url: json['url'] as String,
      key: json['key'] as String,
      text: json['text'] as String,
    );
  }
}

class OcrService {
  static const String _baseUrl = 'https://aws-api.woojeongalex.cloud';

  /// 타입을 실어 보내지 않으면 application/octet-stream으로 S3에 적재돼
  /// 브라우저가 이미지로 열지 못하고 다운로드해 버린다.
  MediaType _mediaType(String filename) {
    final ext = filename.contains('.')
        ? filename.split('.').last.toLowerCase()
        : 'jpg';
    return switch (ext) {
      'png' => MediaType('image', 'png'),
      'gif' => MediaType('image', 'gif'),
      'webp' => MediaType('image', 'webp'),
      'heic' || 'heif' => MediaType('image', 'heic'),
      _ => MediaType('image', 'jpeg'),
    };
  }

  Future<OcrResult> uploadAndOcr({
    required Uint8List bytes,
    required String filename,
  }) async {
    final uri = Uri.parse('$_baseUrl/ocr/upload');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: filename,
          contentType: _mediaType(filename),
        ),
      );

    final streamed = await request.send();
    final body = await streamed.stream.bytesToString();

    if (streamed.statusCode != 200) {
      throw Exception('OCR 실패: $body');
    }

    return OcrResult.fromJson(jsonDecode(body) as Map<String, dynamic>);
  }
}
