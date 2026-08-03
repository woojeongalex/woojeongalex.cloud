package com.ragtailor.stopwatch

import android.app.Activity
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import android.util.TypedValue
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.BaseAdapter
import android.widget.LinearLayout
import android.widget.ListView
import android.widget.TextView
import java.util.Locale

/**
 * `lib/stopwatch_page.dart`의 스톱워치를 안드로이드 네이티브 View로 옮긴 화면.
 *
 * - 큰 숫자로 총 경과 시간을 표시한다 (mm:ss.cc, 1시간 이상이면 h:mm:ss.cc).
 * - 왼쪽 버튼: 실행 중이면 `랩`(스플릿 기록), 정지 상태면 `재설정`.
 * - 오른쪽 버튼: `시작` / `중단`.
 * - 랩 목록은 최신이 위로 쌓이며, 완료된 랩 중 가장 짧은 랩은 초록, 가장 긴 랩은 빨강으로 표시한다.
 *   진행 중인 랩은 색 구분 대상에서 제외한다.
 *
 * XML 레이아웃과 외부 의존성(AppCompat, Compose, RecyclerView) 없이 프레임워크 View만 사용한다.
 * 따라서 `android/app/build.gradle.kts`를 수정하지 않고 그대로 빌드된다.
 */
class StopwatchActivity : Activity() {

    private companion object {
        /** 100분의 1초 표시가 매끄럽게 보이는 갱신 주기. */
        const val TICK_MS = 16L

        const val COLOR_BG = 0xFF000000.toInt()
        const val COLOR_TEXT = 0xFFFFFFFF.toInt()
        const val COLOR_FASTEST = 0xFF30D158.toInt()
        const val COLOR_SLOWEST = 0xFFFF453A.toInt()
        const val COLOR_DIVIDER = 0xFF2C2C2E.toInt()
        const val COLOR_LAP_BTN = 0xFF333333.toInt()
        const val COLOR_STOP_BTN = 0xFF3A181B.toInt()
        const val COLOR_START_BTN = 0xFF0B2E16.toInt()

        /** mm:ss.cc 형식. 1시간을 넘으면 h:mm:ss.cc. */
        fun format(millis: Long): String {
            val hours = millis / 3_600_000
            val minutes = millis / 60_000 % 60
            val seconds = millis / 1_000 % 60
            val centis = millis % 1_000 / 10
            // 로케일에 따라 숫자 표기가 바뀌지 않도록 Locale.US로 고정한다.
            return if (hours > 0) {
                String.format(Locale.US, "%d:%02d:%02d.%02d", hours, minutes, seconds, centis)
            } else {
                String.format(Locale.US, "%02d:%02d.%02d", minutes, seconds, centis)
            }
        }
    }

    // ── 상태 ────────────────────────────────────────────────────────────────

    /** 정지 시점까지 누적된 시간. */
    private var accumulatedMs = 0L

    /** 마지막으로 시작한 시각 (SystemClock 기준). */
    private var startedAt = 0L

    private var running = false

    /** 완료된 랩의 소요 시간 (기록한 순서). */
    private val laps = mutableListOf<Long>()

    /** 현재 진행 중인 랩이 시작된 시점 (총 경과 시간 기준). */
    private var lapStartMs = 0L

    /** 완료된 랩이 2개 이상일 때만 유효한 인덱스. 아니면 -1. */
    private var fastestIndex = -1
    private var slowestIndex = -1

    // ── View ────────────────────────────────────────────────────────────────

    private lateinit var timeView: TextView
    private lateinit var lapButton: TextView
    private lateinit var runButton: TextView
    private lateinit var currentLapRow: LinearLayout
    private lateinit var currentLapLabel: TextView
    private lateinit var currentLapValue: TextView
    private lateinit var lapAdapter: LapAdapter

    private val handler = Handler(Looper.getMainLooper())

    private val ticker = object : Runnable {
        override fun run() {
            renderTime()
            handler.postDelayed(this, TICK_MS)
        }
    }

    /** 총 경과 시간. 시스템 시계 기준이라 프레임이 밀려도 시간이 어긋나지 않는다. */
    private fun elapsedMs(): Long =
        accumulatedMs + if (running) SystemClock.elapsedRealtime() - startedAt else 0L

    private fun hasRecord(): Boolean = running || elapsedMs() > 0L

    // ── 생명주기 ────────────────────────────────────────────────────────────

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(buildContentView())
        render()
    }

    override fun onStart() {
        super.onStart()
        if (running) {
            handler.post(ticker)
        }
    }

    /** 화면이 가려진 동안에는 갱신을 멈춘다. 시계 자체는 계속 흐른다. */
    override fun onStop() {
        handler.removeCallbacks(ticker)
        super.onStop()
    }

    override fun onDestroy() {
        handler.removeCallbacks(ticker)
        super.onDestroy()
    }

    // ── 동작 ────────────────────────────────────────────────────────────────

    /** 시작 ↔ 중단. */
    private fun toggleRun() {
        if (running) {
            accumulatedMs = elapsedMs()
            running = false
            handler.removeCallbacks(ticker)
        } else {
            startedAt = SystemClock.elapsedRealtime()
            running = true
            handler.post(ticker)
        }
        render()
    }

    /** 실행 중이면 랩 기록, 정지 상태면 전체 초기화. */
    private fun lapOrReset() {
        if (running) {
            val now = elapsedMs()
            laps.add(now - lapStartMs)
            lapStartMs = now
            updateLapRanking()
        } else {
            accumulatedMs = 0L
            lapStartMs = 0L
            laps.clear()
            fastestIndex = -1
            slowestIndex = -1
        }
        lapAdapter.notifyDataSetChanged()
        render()
    }

    /** 완료된 랩 중 최단·최장 인덱스를 갱신한다. 랩이 1개뿐이면 구분하지 않는다. */
    private fun updateLapRanking() {
        if (laps.size < 2) {
            fastestIndex = -1
            slowestIndex = -1
            return
        }
        var fastest = 0
        var slowest = 0
        for (i in 1 until laps.size) {
            if (laps[i] < laps[fastest]) fastest = i
            if (laps[i] > laps[slowest]) slowest = i
        }
        fastestIndex = fastest
        slowestIndex = slowest
    }

    // ── 렌더링 ──────────────────────────────────────────────────────────────

    /** 매 틱마다 갱신되는 부분 — 총 경과 시간과 진행 중인 랩. */
    private fun renderTime() {
        val elapsed = elapsedMs()
        timeView.text = format(elapsed)
        currentLapValue.text = format(elapsed - lapStartMs)
    }

    /** 버튼 상태처럼 조작 시점에만 바뀌는 부분. */
    private fun render() {
        renderTime()

        val hasRecord = hasRecord()
        lapButton.text = if (running) "랩" else "재설정"
        lapButton.isEnabled = hasRecord
        lapButton.alpha = if (hasRecord) 1f else 0.4f

        runButton.text = if (running) "중단" else "시작"
        runButton.setTextColor(if (running) COLOR_SLOWEST else COLOR_FASTEST)
        setCircleColor(runButton, if (running) COLOR_STOP_BTN else COLOR_START_BTN)

        currentLapRow.visibility = if (hasRecord) View.VISIBLE else View.GONE
        currentLapLabel.text = "랩 ${laps.size + 1}"
    }

    // ── View 구성 ───────────────────────────────────────────────────────────

    private fun buildContentView(): View {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(COLOR_BG)
            fitsSystemWindows = true
        }

        timeView = TextView(this).apply {
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 64f)
            setTextColor(COLOR_TEXT)
            gravity = Gravity.CENTER
            // 숫자 폭을 고정해 시간이 흔들리지 않게 한다.
            fontFeatureSettings = "tnum"
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                2f,
            )
        }
        root.addView(timeView)

        lapButton = circleButton(COLOR_LAP_BTN, COLOR_TEXT) { lapOrReset() }
        runButton = circleButton(COLOR_START_BTN, COLOR_FASTEST) { toggleRun() }

        val buttonRow = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(32), 0, dp(32), dp(24))
            addView(lapButton)
            // 두 버튼을 좌우 끝으로 밀어내는 빈 공간.
            addView(View(this@StopwatchActivity), LinearLayout.LayoutParams(0, 1, 1f))
            addView(runButton)
        }
        root.addView(buttonRow)
        root.addView(divider(indentDp = 0))

        currentLapRow = lapRow()
        currentLapLabel = currentLapRow.getChildAt(0) as TextView
        currentLapValue = currentLapRow.getChildAt(1) as TextView
        root.addView(currentLapRow)

        lapAdapter = LapAdapter()
        val listView = ListView(this).apply {
            adapter = lapAdapter
            divider = null
            dividerHeight = 0
            isVerticalScrollBarEnabled = false
            layoutParams = LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                3f,
            )
        }
        root.addView(listView)

        return root
    }

    private fun circleButton(background: Int, foreground: Int, onClick: () -> Unit): TextView {
        val size = dp(84)
        return TextView(this).apply {
            gravity = Gravity.CENTER
            setTextSize(TypedValue.COMPLEX_UNIT_SP, 18f)
            setTextColor(foreground)
            isClickable = true
            layoutParams = LinearLayout.LayoutParams(size, size)
            setOnClickListener { onClick() }
            setCircleColor(this, background)
        }
    }

    private fun setCircleColor(view: TextView, color: Int) {
        view.background = GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(color)
        }
    }

    /** 랩 한 줄 — 왼쪽 라벨, 오른쪽 시간. */
    private fun lapRow(): LinearLayout {
        val row = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            setPadding(dp(20), dp(14), dp(20), dp(14))
        }
        row.addView(
            lapText(),
            LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f),
        )
        row.addView(
            lapText().apply { gravity = Gravity.END },
            LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f),
        )
        return row
    }

    private fun lapText(): TextView = TextView(this).apply {
        setTextSize(TypedValue.COMPLEX_UNIT_SP, 17f)
        setTextColor(COLOR_TEXT)
        fontFeatureSettings = "tnum"
    }

    private fun divider(indentDp: Int): View = View(this).apply {
        setBackgroundColor(COLOR_DIVIDER)
        layoutParams = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            1,
        ).apply { leftMargin = dp(indentDp) }
    }

    private fun dp(value: Int): Int = (value * resources.displayMetrics.density).toInt()

    // ── 완료된 랩 목록 ──────────────────────────────────────────────────────

    /** 최신 랩이 위로 오도록 역순으로 노출한다. */
    private inner class LapAdapter : BaseAdapter() {

        override fun getCount(): Int = laps.size

        override fun getItem(position: Int): Long = laps[laps.size - 1 - position]

        override fun getItemId(position: Int): Long = (laps.size - 1 - position).toLong()

        override fun getView(position: Int, convertView: View?, parent: ViewGroup?): View {
            val container = convertView as? LinearLayout
                ?: LinearLayout(this@StopwatchActivity).apply {
                    orientation = LinearLayout.VERTICAL
                    addView(divider(indentDp = 20))
                    addView(lapRow())
                }

            val row = container.getChildAt(1) as LinearLayout
            val label = row.getChildAt(0) as TextView
            val value = row.getChildAt(1) as TextView

            val lapIndex = laps.size - 1 - position
            val color = when (lapIndex) {
                fastestIndex -> COLOR_FASTEST
                slowestIndex -> COLOR_SLOWEST
                else -> COLOR_TEXT
            }

            label.text = "랩 ${lapIndex + 1}"
            label.setTextColor(color)
            value.text = format(laps[lapIndex])
            value.setTextColor(color)

            return container
        }
    }
}
