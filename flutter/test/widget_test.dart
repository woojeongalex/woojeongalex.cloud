import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:taper/main.dart';

void main() {
  testWidgets('intro screen renders key content', (WidgetTester tester) async {
    // 앱의 home은 인트로 영상 화면으로 바뀌었으므로 소개 화면을 직접 띄운다.
    await tester.pumpWidget(const MaterialApp(home: IntroScreen()));
    await tester.pumpAndSettle();

    expect(find.text('AI 서비스 개발'), findsOneWidget);
    expect(find.text('교육'), findsWidgets);
    expect(find.text('CURRICULUM'), findsOneWidget);
    expect(find.text('모집 개요'), findsOneWidget);
    expect(find.text('CONTACT'), findsOneWidget);
  });

  testWidgets('curriculum tags are rendered', (WidgetTester tester) async {
    // 앱의 home은 인트로 영상 화면으로 바뀌었으므로 소개 화면을 직접 띄운다.
    await tester.pumpWidget(const MaterialApp(home: IntroScreen()));
    await tester.pumpAndSettle();

    expect(find.text('FastAPI'), findsOneWidget);
    expect(find.text('RAG'), findsOneWidget);
    expect(find.text('Python'), findsOneWidget);
  });
}
