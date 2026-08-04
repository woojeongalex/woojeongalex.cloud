import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:kakao_flutter_sdk_user/kakao_flutter_sdk_user.dart';
import 'package:video_player/video_player.dart';

import 'home_page.dart';
import 'login_page.dart';
import 'services/auth_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  const nativeAppKey = String.fromEnvironment('KAKAO_NATIVE_APP_KEY');
  const jsAppKey = String.fromEnvironment('KAKAO_JS_APP_KEY');
  KakaoSdk.init(nativeAppKey: nativeAppKey, javaScriptAppKey: jsAppKey);
  runApp(const TaperApp());
}

class TaperApp extends StatelessWidget {
  const TaperApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AX Academy',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: Colors.white,
        useMaterial3: true,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0A0A),
        useMaterial3: true,
      ),
      themeMode: ThemeMode.system,
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  final AuthService _auth = AuthService();
  bool? _loggedIn;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final loggedIn = await _auth.isLoggedIn();
    if (!mounted) return;
    setState(() => _loggedIn = loggedIn);
  }

  void _onLoginSuccess() {
    setState(() => _loggedIn = true);
  }

  @override
  Widget build(BuildContext context) {
    if (_loggedIn == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    if (_loggedIn!) {
      return const VideoIntroScreen();
    }
    return LoginPage(onLoginSuccess: _onLoginSuccess);
  }
}

/// 인트로 영상을 재생하고 4초 뒤 스톱워치 화면으로 넘어간다.
///
/// 영상이 4초보다 길어도 4초에 전환하고, 영상 로드에 실패해도 그냥 넘어간다.
/// 인트로 때문에 앱이 멈춰 있는 상황을 만들지 않는다.
class VideoIntroScreen extends StatefulWidget {
  const VideoIntroScreen({super.key});

  @override
  State<VideoIntroScreen> createState() => _VideoIntroScreenState();
}

class _VideoIntroScreenState extends State<VideoIntroScreen> {
  static const String _videoAsset = 'assets/video/intro.mp4';
  static const Duration _introDuration = Duration(seconds: 5);

  final VideoPlayerController _controller = VideoPlayerController.asset(
    _videoAsset,
  );
  Timer? _timer;
  bool _navigated = false;

  @override
  void initState() {
    super.initState();
    _playIntro();
    _timer = Timer(_introDuration, _goToHome);
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  Future<void> _playIntro() async {
    try {
      await _controller.initialize();
      if (!mounted) {
        return;
      }
      await _controller.setVolume(0);
      await _controller.play();
      setState(() {});
    } on Object {
      _goToHome();
    }
  }

  void _goToHome() {
    if (_navigated || !mounted) {
      return;
    }
    _navigated = true;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => const HomePage()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: _controller.value.isInitialized
          ? SizedBox.expand(
              // 화면 비율이 달라도 여백 없이 꽉 채운다.
              child: FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: _controller.value.size.width,
                  height: _controller.value.size.height,
                  child: VideoPlayer(_controller),
                ),
              ),
            )
          : const SizedBox.expand(),
    );
  }
}

class IntroScreen extends StatelessWidget {
  const IntroScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _HeroSection(),
              _CurriculumSection(),
              _OverviewSection(),
              _ContactSection(),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────

Color _textPrimary(bool isDark) =>
    isDark ? const Color(0xFFF1F5F9) : const Color(0xFF0F172A);

Color _textSecondary(bool isDark) =>
    isDark ? const Color(0xFF94A3B8) : const Color(0xFF475569);

Color _textMuted(bool isDark) =>
    isDark ? const Color(0xFF6B7280) : const Color(0xFF9CA3AF);

Color _borderColor(bool isDark) =>
    isDark ? const Color(0xFF1F2937) : const Color(0xFFE5E7EB);

Color _cardBg(bool isDark) =>
    isDark ? const Color(0xFF111111) : const Color(0xFFF9FAFB);

// ── Hero ─────────────────────────────────────────────────────────────────────

class _HeroSection extends StatelessWidget {
  const _HeroSection();

  static const _tags = [
    'FastAPI',
    'RAG',
    'Multi-Agent',
    'LangChain',
    'Python',
    '실습 프로젝트',
    '엔터프라이즈 AI',
    '클린 아키텍처',
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      color: isDark ? const Color(0xFF0A0A0A) : Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 64),
      child: Column(
        children: [
          Text(
            '글로벌 기업 IBM × Red Hat과 함께하는',
            style: TextStyle(
              fontSize: 13,
              color: _textSecondary(isDark),
              height: 1.5,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            decoration: BoxDecoration(
              border: Border.all(color: _borderColor(isDark)),
            ),
            child: Text(
              'IBM  ×  Red Hat',
              style: TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w600,
                letterSpacing: 2.5,
                color: isDark
                    ? const Color(0xFFD1D5DB)
                    : const Color(0xFF1F2937),
              ),
            ),
          ),
          const SizedBox(height: 36),
          ShaderMask(
            shaderCallback: (bounds) => const LinearGradient(
              colors: [Color(0xFF0284C7), Color(0xFF0EA5E9), Color(0xFF0891B2)],
            ).createShader(bounds),
            child: const Text(
              'AI 서비스 개발',
              style: TextStyle(
                fontSize: 42,
                fontWeight: FontWeight.w800,
                color: Colors.white,
                height: 1.1,
                letterSpacing: -0.5,
              ),
              textAlign: TextAlign.center,
            ),
          ),
          Text(
            '교육',
            style: TextStyle(
              fontSize: 42,
              fontWeight: FontWeight.w800,
              color: _textPrimary(isDark),
              height: 1.1,
              letterSpacing: -0.5,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          for (final line in const [
            'K-Digital Training',
            '디지털 선도기업 아카데미',
            '[IBM x RedHat]',
          ])
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Text(
                line,
                style: TextStyle(
                  fontSize: 15,
                  color: _textSecondary(isDark),
                  height: 1.6,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          Text(
            'AI Transformation - AX Academy',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w600,
              color: _textPrimary(isDark),
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),
          Wrap(
            alignment: WrapAlignment.center,
            spacing: 8,
            runSpacing: 8,
            children: _tags
                .map((tag) => _Tag(label: tag, isDark: isDark))
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  const _Tag({required this.label, required this.isDark});
  final String label;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF111111) : Colors.white,
        border: Border.all(color: _borderColor(isDark)),
        borderRadius: BorderRadius.circular(999),
        boxShadow: isDark
            ? null
            : [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.06),
                  blurRadius: 4,
                  offset: const Offset(0, 1),
                ),
              ],
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: _textSecondary(isDark),
        ),
      ),
    );
  }
}

// ── Curriculum ────────────────────────────────────────────────────────────────

class _CurriculumSection extends StatelessWidget {
  const _CurriculumSection();

  static const _items = [
    ('Python\n기초', 'Fundamentals', false),
    ('FastAPI\n백엔드', 'Backend', false),
    ('RAG\n시스템', 'RAG System', false),
    ('Multi\nAgent', 'Multi-Agent', false),
    ('LangChain\n활용', 'LangChain', false),
    ('클린\n아키텍처', 'Architecture', false),
    ('엔터프라이즈\nAI', 'Enterprise AI', true),
    ('실습\n프로젝트', 'Project', false),
    ('DevOps\nCI/CD', 'DevOps', false),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      color: isDark ? const Color(0xFF0A0A0A) : Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 40),
      child: Column(
        children: [
          Text(
            'CURRICULUM',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              letterSpacing: 3.0,
              color: _textMuted(isDark),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '교육 과정',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              letterSpacing: 1.5,
              color: _textPrimary(isDark),
            ),
          ),
          const SizedBox(height: 24),
          GridView.count(
            crossAxisCount: 3,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 4,
            crossAxisSpacing: 4,
            children: _items
                .map(
                  (item) => _CurriculumCell(
                    title: item.$1,
                    subtitle: item.$2,
                    featured: item.$3,
                    isDark: isDark,
                  ),
                )
                .toList(),
          ),
        ],
      ),
    );
  }
}

class _CurriculumCell extends StatelessWidget {
  const _CurriculumCell({
    required this.title,
    required this.subtitle,
    required this.featured,
    required this.isDark,
  });
  final String title;
  final String subtitle;
  final bool featured;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    final bgColor = featured
        ? (isDark ? const Color(0xFF1E3A5F) : const Color(0xFFEFF6FF))
        : _cardBg(isDark);
    final borderC = featured
        ? (isDark ? const Color(0xFF1D4ED8) : const Color(0xFF93C5FD))
        : _borderColor(isDark);
    final titleColor = featured
        ? (isDark ? const Color(0xFFBFDBFE) : const Color(0xFF1E40AF))
        : _textPrimary(isDark);
    final subtitleColor = featured
        ? const Color(0xFF60A5FA)
        : _textMuted(isDark);

    return Container(
      decoration: BoxDecoration(
        color: bgColor,
        border: Border.all(color: borderC),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 9,
              letterSpacing: 1.2,
              color: subtitleColor,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          Text(
            title,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: titleColor,
              height: 1.3,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// ── Overview ──────────────────────────────────────────────────────────────────

class _OverviewSection extends StatelessWidget {
  const _OverviewSection();

  static const _details = [
    (
      Icons.cloud_outlined,
      '교육과정',
      '[IBM x RedHat] AI Transformation - AX Academy',
    ),
    (Icons.calendar_today_outlined, '개강일정', '(8기) 7월 예정'),
    (Icons.business_outlined, '교육장소', '하이미디어 추후 공지'),
    (Icons.access_time_outlined, '학습시간', '매주 월~금 (am09:30 ~ pm18:30까지)'),
    (Icons.slideshow_outlined, '교육방법', '오프라인 수업'),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF0A0A0A) : Colors.white,
        border: Border(top: BorderSide(color: _borderColor(isDark))),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 56),
      child: Column(
        children: [
          Text(
            '모집 개요',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w700,
              letterSpacing: -0.3,
              color: _textPrimary(isDark),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          for (final line in const [
            'K-Digital Training',
            '디지털 선도기업 아카데미',
            '[IBM x RedHat]',
            'AI Transformation - AX Academy',
          ])
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Text(
                line,
                style: TextStyle(
                  fontSize: 14,
                  color: _textSecondary(isDark),
                  height: 1.6,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          const SizedBox(height: 40),
          Container(
            decoration: BoxDecoration(
              border: Border(top: BorderSide(color: _borderColor(isDark))),
            ),
            child: Column(
              children: _details
                  .map(
                    (d) => _DetailRow(
                      icon: d.$1,
                      label: d.$2,
                      value: d.$3,
                      isDark: isDark,
                    ),
                  )
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
    required this.isDark,
  });
  final IconData icon;
  final String label;
  final String value;
  final bool isDark;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: _borderColor(isDark))),
      ),
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: _textMuted(isDark)),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: _textPrimary(isDark),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 14,
                    color: _textSecondary(isDark),
                    height: 1.5,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ── Contact ───────────────────────────────────────────────────────────────────

class _ContactSection extends StatelessWidget {
  const _ContactSection();

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF0A0A0A) : Colors.white,
        border: Border(top: BorderSide(color: _borderColor(isDark))),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 64),
      child: Column(
        children: [
          Text(
            'CONTACT',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              letterSpacing: 3.0,
              color: _textMuted(isDark),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            '교육 문의',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w500,
              letterSpacing: -0.2,
              color: _textPrimary(isDark),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'AI 서비스 개발 교육 일정·커리큘럼 문의는\n아래 이메일로 연락주세요.',
            style: TextStyle(
              fontSize: 14,
              color: _textSecondary(isDark),
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          _EmailButton(isDark: isDark),
        ],
      ),
    );
  }
}

class _EmailButton extends StatelessWidget {
  const _EmailButton({required this.isDark});
  final bool isDark;

  static const _email = 'rex@ragwatson.com';

  void _onTap(BuildContext context) {
    Clipboard.setData(const ClipboardData(text: _email));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('이메일이 클립보드에 복사됐습니다'),
        backgroundColor: isDark
            ? const Color(0xFF1F2937)
            : const Color(0xFF111827),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final borderC = isDark ? const Color(0xFFF1F5F9) : const Color(0xFF111827);
    final textColor = isDark
        ? const Color(0xFFF1F5F9)
        : const Color(0xFF111827);

    return GestureDetector(
      onTap: () => _onTap(context),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
        decoration: BoxDecoration(border: Border.all(color: borderC)),
        child: Text(
          _email,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w500,
            letterSpacing: 1.5,
            color: textColor,
          ),
        ),
      ),
    );
  }
}
