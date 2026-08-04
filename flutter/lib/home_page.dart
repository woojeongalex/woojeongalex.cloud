import 'package:flutter/material.dart';

import 'camera_page.dart';
import 'stopwatch_page.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  int _currentIndex = 0;

  static const _pages = <Widget>[StopwatchPage(), CameraPage()];

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final barBg = isDark ? const Color(0xFF111111) : Colors.white;
    final border = isDark ? const Color(0xFF383838) : const Color(0xFFE5E5E5);

    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _pages),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          color: barBg,
          border: Border(top: BorderSide(color: border, width: 0.5)),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (i) => setState(() => _currentIndex = i),
          backgroundColor: barBg,
          elevation: 0,
          selectedItemColor: isDark ? Colors.white : const Color(0xFF171717),
          unselectedItemColor: isDark
              ? const Color(0xFF737373)
              : const Color(0xFFA3A3A3),
          selectedFontSize: 12,
          unselectedFontSize: 12,
          type: BottomNavigationBarType.fixed,
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.timer_outlined),
              activeIcon: Icon(Icons.timer),
              label: '스톱워치',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.camera_alt_outlined),
              activeIcon: Icon(Icons.camera_alt),
              label: '카메라 OCR',
            ),
          ],
        ),
      ),
    );
  }
}
