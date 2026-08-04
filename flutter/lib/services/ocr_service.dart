import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;

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

  Future<OcrResult> uploadAndOcr({
    required Uint8List bytes,
    required String filename,
  }) async {
    final uri = Uri.parse('$_baseUrl/silicon_valley/s3-image/upload-ocr');
    final request = http.MultipartRequest('POST', uri)
      ..files.add(
        http.MultipartFile.fromBytes('file', bytes, filename: filename),
      );

    final streamed = await request.send();
    final body = await streamed.stream.bytesToString();

    if (streamed.statusCode != 200) {
      throw Exception('OCR 실패: $body');
    }

    return OcrResult.fromJson(jsonDecode(body) as Map<String, dynamic>);
  }
}
