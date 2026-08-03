import 'package:flutter/material.dart';

/// 단독 실행용 엔트리포인트.
/// `flutter run -t lib/counter_page.dart`
void main() {
  runApp(const CounterDemoApp());
}

class CounterDemoApp extends StatelessWidget {
  const CounterDemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '카운터 앱',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue),
      home: const CounterPage(),
    );
  }
}

/// 버튼을 누른 횟수를 세는 연습용 화면.
class CounterPage extends StatefulWidget {
  const CounterPage({super.key});

  @override
  State<CounterPage> createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('플러터 카운터 예제')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('버튼을 누른 횟수:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: '증가',
        child: const Icon(Icons.add),
      ),
    );
  }
}
