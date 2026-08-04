package cloud.woojeongalex.stopwatch

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

class StopwatchActivity : Activity() {

    private companion object {
        const val TICK_MS = 16L

        const val COLOR_BG = 0xFF000000.toInt()
        const val COLOR_TEXT = 0xFFFFFFFF.toInt()
        const val COLOR_FASTEST = 0xFF30D158.toInt()
        const val COLOR_SLOWEST = 0xFFFF453A.toInt()
        const val COLOR_DIVIDER = 0xFF2C2C2E.toInt()
        const val COLOR_LAP_BTN = 0xFF333333.toInt()
        const val COLOR_STOP_BTN = 0xFF3A181B.toInt()
        const val COLOR_START_BTN = 0xFF0B2E16.toInt()

        fun format(millis: Long): String {
            val hours = millis / 3_600_000
            val minutes = millis / 60_000 % 60
            val seconds = millis / 1_000 % 60
            val centis = millis % 1_000 / 10
            return if (hours > 0) {
                String.format(Locale.US, "%d:%02d:%02d.%02d", hours, minutes, seconds, centis)
            } else {
                String.format(Locale.US, "%02d:%02d.%02d", minutes, seconds, centis)
            }
        }
    }

    private var accumulatedMs = 0L
    private var startedAt = 0L
    private var running = false
    private val laps = mutableListOf<Long>()
    private var lapStartMs = 0L
    private var fastestIndex = -1
    private var slowestIndex = -1

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

    private fun elapsedMs(): Long =
        accumulatedMs + if (running) SystemClock.elapsedRealtime() - startedAt else 0L

    private fun hasRecord(): Boolean = running || elapsedMs() > 0L

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

    override fun onStop() {
        handler.removeCallbacks(ticker)
        super.onStop()
    }

    override fun onDestroy() {
        handler.removeCallbacks(ticker)
        super.onDestroy()
    }

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

    private fun renderTime() {
        val elapsed = elapsedMs()
        timeView.text = format(elapsed)
        currentLapValue.text = format(elapsed - lapStartMs)
    }

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
