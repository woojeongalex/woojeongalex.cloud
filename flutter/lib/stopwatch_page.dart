import 'dart:async';

import 'package:flutter/material.dart';

import 'counter_page.dart';

/// 단독 실행용 엔트리포인트.
/// `flutter run -t lib/stopwatch_page.dart`
void main() {
  runApp(const StopwatchApp());
}

class StopwatchApp extends StatelessWidget {
  const StopwatchApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '스톱워치',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: Colors.black,
        useMaterial3: true,
      ),
      home: const StopwatchPage(),
    );
  }
}

/// iOS 스톱워치 형태의 위젯.
///
/// - 큰 숫자로 총 경과 시간을 표시한다 (mm:ss.cc, 1시간 이상이면 h:mm:ss.cc).
/// - 왼쪽 버튼: 실행 중이면 `랩`(스플릿 기록), 정지 상태면 `재설정`.
/// - 오른쪽 버튼: `시작` / `중단`.
/// - 랩 목록은 최신이 위로 쌓이며, 완료된 랩 중 가장 짧은 랩은 초록, 가장 긴 랩은 빨강으로 표시한다.
class StopwatchPage extends StatefulWidget {
  const StopwatchPage({super.key});

  @override
  State<StopwatchPage> createState() => _StopwatchPageState();
}

class _StopwatchPageState extends State<StopwatchPage> {
  /// 100분의 1초 단위 표시가 매끄럽게 보이는 주기.
  static const Duration _tickInterval = Duration(milliseconds: 16);

  static const Color _fastest = Color(0xFF30D158);
  static const Color _slowest = Color(0xFFFF453A);
  static const Color _divider = Color(0xFF2C2C2E);

  final Stopwatch _stopwatch = Stopwatch();
  Timer? _ticker;

  /// 완료된 랩의 소요 시간 (기록한 순서).
  final List<Duration> _laps = <Duration>[];

  /// 현재 진행 중인 랩이 시작된 시점 (총 경과 시간 기준).
  Duration _lapStart = Duration.zero;

  bool get _isRunning => _stopwatch.isRunning;

  Duration get _elapsed => _stopwatch.elapsed;

  /// 진행 중인 랩의 소요 시간.
  Duration get _currentLap => _elapsed - _lapStart;

  @override
  void dispose() {
    _ticker?.cancel();
    _stopwatch.stop();
    super.dispose();
  }

  void _toggleRun() {
    if (_isRunning) {
      _stopwatch.stop();
      _ticker?.cancel();
      _ticker = null;
    } else {
      _stopwatch.start();
      _ticker = Timer.periodic(_tickInterval, (_) => setState(() {}));
    }
    setState(() {});
  }

  /// 실행 중이면 랩 기록, 정지 상태면 전체 초기화.
  void _lapOrReset() {
    setState(() {
      if (_isRunning) {
        _laps.add(_currentLap);
        _lapStart = _elapsed;
      } else {
        _stopwatch.reset();
        _laps.clear();
        _lapStart = Duration.zero;
      }
    });
  }

  /// `mm:ss.cc` 형식. 1시간을 넘으면 `h:mm:ss.cc`.
  static String _format(Duration d) {
    final String minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final String seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    final String centis = (d.inMilliseconds.remainder(1000) ~/ 10)
        .toString()
        .padLeft(2, '0');
    if (d.inHours > 0) {
      return '${d.inHours}:$minutes:$seconds.$centis';
    }
    return '$minutes:$seconds.$centis';
  }

  @override
  Widget build(BuildContext context) {
    // 완료된 랩이 2개 이상일 때만 최단·최장을 구분한다 (진행 중인 랩은 제외).
    int fastestIndex = -1;
    int slowestIndex = -1;
    if (_laps.length >= 2) {
      fastestIndex = 0;
      slowestIndex = 0;
      for (int i = 1; i < _laps.length; i++) {
        if (_laps[i] < _laps[fastestIndex]) {
          fastestIndex = i;
        }
        if (_laps[i] > _laps[slowestIndex]) {
          slowestIndex = i;
        }
      }
    }

    final bool hasRecord = _isRunning || _elapsed > Duration.zero;

    return Scaffold(
      // 밝은 테마의 앱에서 열려도 배경이 흰색이 되지 않도록 고정한다.
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black,
        elevation: 0,
        actions: <Widget>[
          IconButton(
            icon: const Icon(Icons.add_circle_outline, color: Colors.white),
            tooltip: '카운터 예제 열기',
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute<void>(builder: (_) => const CounterPage()),
              );
            },
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: <Widget>[
            Expanded(
              flex: 2,
              child: Center(
                child: Text(
                  _format(_elapsed),
                  style: const TextStyle(
                    fontSize: 72,
                    fontWeight: FontWeight.w200,
                    color: Colors.white,
                    // 숫자 폭을 고정해 시간이 흔들리지 않게 한다.
                    fontFeatures: <FontFeature>[FontFeature.tabularFigures()],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  _CircleButton(
                    label: _isRunning ? '랩' : '재설정',
                    background: const Color(0xFF333333),
                    foreground: Colors.white,
                    onPressed: hasRecord ? _lapOrReset : null,
                  ),
                  _CircleButton(
                    label: _isRunning ? '중단' : '시작',
                    background: _isRunning
                        ? const Color(0xFF3A181B)
                        : const Color(0xFF0B2E16),
                    foreground: _isRunning ? _slowest : _fastest,
                    onPressed: _toggleRun,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            const Divider(height: 1, color: _divider),
            Expanded(
              flex: 3,
              child: ListView.separated(
                padding: EdgeInsets.zero,
                // 진행 중인 랩 1개 + 완료된 랩들.
                itemCount: hasRecord ? _laps.length + 1 : 0,
                separatorBuilder: (_, _) =>
                    const Divider(height: 1, indent: 20, color: _divider),
                itemBuilder: (BuildContext context, int index) {
                  // index 0 = 진행 중인 랩, 그 아래로 최신 완료 랩부터 역순.
                  if (index == 0) {
                    return _LapTile(
                      number: _laps.length + 1,
                      duration: _currentLap,
                      color: Colors.white,
                    );
                  }
                  final int lapIndex = _laps.length - index;
                  Color color = Colors.white;
                  if (lapIndex == fastestIndex) {
                    color = _fastest;
                  } else if (lapIndex == slowestIndex) {
                    color = _slowest;
                  }
                  return _LapTile(
                    number: lapIndex + 1,
                    duration: _laps[lapIndex],
                    color: color,
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LapTile extends StatelessWidget {
  const _LapTile({
    required this.number,
    required this.duration,
    required this.color,
  });

  final int number;
  final Duration duration;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final TextStyle style = TextStyle(
      fontSize: 17,
      color: color,
      fontFeatures: const <FontFeature>[FontFeature.tabularFigures()],
    );
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: <Widget>[
          Text('랩 $number', style: style),
          Text(_StopwatchPageState._format(duration), style: style),
        ],
      ),
    );
  }
}

class _CircleButton extends StatelessWidget {
  const _CircleButton({
    required this.label,
    required this.background,
    required this.foreground,
    required this.onPressed,
  });

  final String label;
  final Color background;
  final Color foreground;

  /// null이면 비활성 상태로 흐리게 표시한다.
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    final double opacity = onPressed == null ? 0.4 : 1.0;
    return SizedBox(
      width: 84,
      height: 84,
      child: Material(
        color: background.withValues(alpha: opacity),
        shape: const CircleBorder(),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: onPressed,
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 18,
                color: foreground.withValues(alpha: opacity),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
