log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- 1. ModernChart.kt: his Curve + scrub gesture, adapted ----------
open("app/src/main/java/com/davidtakac/bura/graphs/common/ModernChart.kt", "w").write(
'''/*
 * Monotone cubic interpolation and scrub gesture adapted from Stratus
 * (https://github.com/Yigder/stratus), Copyright (C) 2026 Yigder, GPL-3.0-or-later.
 * Ported to Pluvia. Both projects are GPLv3.
 */

package com.davidtakac.bura.graphs.common

import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.input.pointer.positionChange
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.math.abs
import kotlin.math.floor
import kotlin.math.sqrt

/**
 * Monotone cubic (Fritsch-Carlson) through hourly values: smooth, never
 * overshooting a peak or dipping below zero between points.
 */
class Curve(private val values: List<Double>) {
    private val m = DoubleArray(values.size)

    init {
        if (values.size < 2) return
        val d = DoubleArray(values.size - 1) { values[it + 1] - values[it] }
        m[0] = d[0]
        m[values.size - 1] = d[d.size - 1]
        for (k in 1 until values.size - 1) {
            m[k] = if (d[k - 1] * d[k] <= 0.0) 0.0 else (d[k - 1] + d[k]) / 2
        }
        for (k in 0 until values.size - 1) {
            val dk = d[k]
            if (dk == 0.0) { m[k] = 0.0; m[k + 1] = 0.0; continue }
            val a = m[k] / dk
            val b = m[k + 1] / dk
            val h = a * a + b * b
            if (h > 9) {
                val t = 3 / sqrt(h)
                m[k] = t * a * dk
                m[k + 1] = t * b * dk
            }
        }
    }

    /** Value on the curve at fractional index [s]. */
    fun at(s: Float): Double {
        if (values.isEmpty()) return 0.0
        val i0 = floor(s).toInt().coerceIn(0, values.size - 1)
        val i1 = (i0 + 1).coerceAtMost(values.size - 1)
        if (i1 == i0) return values[i0]
        val t = (s - i0).toDouble().coerceIn(0.0, 1.0)
        val t2 = t * t
        val t3 = t2 * t
        return (2 * t3 - 3 * t2 + 1) * values[i0] +
            (t3 - 2 * t2 + t) * m[i0] +
            (-2 * t3 + 3 * t2) * values[i1] +
            (t3 - t2) * m[i1]
    }

    /** Traces the smooth curve through pixel coordinates [xs]/[ys] into [path],
     *  and the area between the curve and [baseY] into [area]. */
    fun trace(xs: List<Float>, ys: List<Float>, path: Path, area: Path, baseY: Float) {
        if (xs.isEmpty()) return
        path.moveTo(xs[0], ys[0])
        area.moveTo(xs[0], baseY)
        area.lineTo(xs[0], ys[0])
        for (i in 0 until xs.size - 1) {
            val x0 = xs[i]; val x1 = xs[i + 1]
            val y0 = ys[i]; val y1 = ys[i + 1]
            if (values[i + 1] == values[i]) {
                path.lineTo(x1, y1); area.lineTo(x1, y1); continue
            }
            val scale = ((y1 - y0) / (values[i + 1] - values[i]).toFloat())
            val dx = (x1 - x0) / 3
            val c1y = y0 + (m[i] / 3).toFloat() * scale
            val c2y = y1 - (m[i + 1] / 3).toFloat() * scale
            path.cubicTo(x0 + dx, c1y, x1 - dx, c2y, x1, y1)
            area.cubicTo(x0 + dx, c1y, x1 - dx, c2y, x1, y1)
        }
        area.lineTo(xs[xs.size - 1], baseY)
        area.close()
    }
}

/**
 * Press-and-drag scrubbing that coexists with vertical scrolling: a sideways
 * drag or a ~140 ms hold scrubs and consumes; a vertical drag is left for the
 * scroll view. Reports the finger's x, then null on release.
 */
fun Modifier.scrubGesture(onScrub: (Float?) -> Unit): Modifier = pointerInput(Unit) {
    awaitEachGesture {
        val down = awaitFirstDown(requireUnconsumed = false)
        val slop = viewConfiguration.touchSlop
        var x = down.position.x
        val scrubbing = withTimeoutOrNull(140L) {
            var total = Offset.Zero
            while (true) {
                val c = awaitPointerEvent().changes.firstOrNull { it.id == down.id } ?: return@withTimeoutOrNull false
                if (!c.pressed) return@withTimeoutOrNull false
                total += c.positionChange()
                x = c.position.x
                if (abs(total.x) > slop && abs(total.x) > abs(total.y)) { c.consume(); return@withTimeoutOrNull true }
                if (abs(total.y) > slop) return@withTimeoutOrNull false
            }
            false
        } ?: true
        if (!scrubbing) return@awaitEachGesture
        onScrub(x)
        while (true) {
            val c = awaitPointerEvent().changes.firstOrNull { it.id == down.id } ?: break
            if (!c.pressed) break
            c.consume()
            onScrub(c.position.x)
        }
        onScrub(null)
    }
}
''')
ok("ModernChart.kt created (Curve + scrubGesture)")

# ---------- 2. WindGraph: modernized in place ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/wind/compose/WindGraph.kt"
s = open(p).read()

anchor = "import com.davidtakac.bura.graphs.wind.WindGraph"
s2 = s.replace(anchor, anchor +
    "\nimport androidx.compose.ui.graphics.Brush"
    "\nimport androidx.compose.ui.graphics.Color"
    "\nimport androidx.compose.ui.graphics.StrokeCap"
    "\nimport androidx.compose.ui.graphics.StrokeJoin"
    "\nimport androidx.compose.ui.geometry.Size"
    "\nimport com.davidtakac.bura.graphs.common.Curve"
    "\nimport com.davidtakac.bura.graphs.common.scrubGesture")
if s2 != s: ok("WindGraph: imports added"); s = s2
else: warn("WindGraph: import anchor not found")

NEW_WIND = '''@Composable
fun WindGraph(
    state: WindGraph,
    max: WindSpeed,


    modifier: Modifier = Modifier
) {
    if (state.points.isEmpty()) {
        Box(modifier = modifier, contentAlignment = Alignment.Center) {
            Text(
                text = "No data",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
        return
    }
    val points = state.points
    val now = remember { ZonedDateTime.now() }
    val primary = MaterialTheme.colorScheme.primary
    val onSurfaceVariant = MaterialTheme.colorScheme.onSurfaceVariant
    val timeFormatter = remember { DateTimeFormatter.ofPattern("HH:mm") }
    val measurer = rememberTextMeasurer()
    val curve = remember(state) { Curve(points.map { it.speed.value }) }
    val maxIdx = points.indices.maxByOrNull { points[it].speed.value } ?: 0
    var scrub by remember(state) { mutableStateOf<Float?>(null) }

    Column(modifier = modifier.padding(10.dp)) {
        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .scrubGesture { x ->
                    scrub = x?.let { px ->
                        val usable = size.width.toFloat()
                        val step = if (points.size > 1) usable / (points.size - 1) else usable
                        (px / step).coerceIn(0f, points.lastIndex.toFloat())
                    }
                }
        ) {
            val axisTop = 16.dp.toPx()
            val axisBottom = 18.dp.toPx()
            val plotH = size.height - axisTop - axisBottom
            if (plotH <= 0f) return@Canvas
            val maxVal = max.value.takeIf { it > 0.0 } ?: 1.0
            val step = if (points.size > 1) size.width / (points.size - 1) else 0f
            fun x(i: Int) = i * step
            fun y(v: Double) = axisTop + plotH - (v / maxVal * plotH).toFloat()

            val xs = points.indices.map { x(it) }
            val ys = points.map { y(it.speed.value) }
            val linePath = Path()
            val fillPath = Path()
            curve.trace(xs, ys, linePath, fillPath, baseY = axisTop + plotH)

            drawPath(
                path = fillPath,
                brush = Brush.verticalGradient(
                    colors = listOf(primary.copy(alpha = 0.30f), primary.copy(alpha = 0.03f)),
                    startY = axisTop,
                    endY = axisTop + plotH
                )
            )
            drawPath(
                path = linePath,
                brush = Brush.verticalGradient(
                    colors = listOf(primary, primary.copy(alpha = 0.55f)),
                    startY = axisTop,
                    endY = axisTop + plotH
                ),
                style = Stroke(width = 3.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
            )

            val nowIdx = points.indexOfLast { !it.datetime.isAfter(now) }
            if (nowIdx in 0 until points.lastIndex) {
                val nx = x(nowIdx)
                drawLine(
                    color = onSurfaceVariant,
                    start = Offset(nx, axisTop),
                    end = Offset(nx, axisTop + plotH),
                    strokeWidth = 1.dp.toPx(),
                    pathEffect = PathEffect.dashPathEffect(floatArrayOf(4f, 4f))
                )
                drawRect(
                    color = Color.Black.copy(alpha = 0.05f),
                    topLeft = Offset(0f, axisTop),
                    size = Size(nx, plotH)
                )
            }
            points.forEachIndexed { i, p ->
                if (p.datetime.hour % 6 == 0) {
                    drawText(
                        textMeasurer = measurer,
                        text = p.datetime.format(timeFormatter),
                        topLeft = Offset(x(i) - 15.dp.toPx(), size.height - axisBottom + 2.dp.toPx()),
                        style = TextStyle(fontSize = 9.sp, color = onSurfaceVariant)
                    )
                }
            }
            val maxLabel = measurer.measure(
                points[maxIdx].speed.string(),
                TextStyle(fontSize = 10.sp, color = onSurfaceVariant)
            )
            drawText(
                textLayoutResult = maxLabel,
                topLeft = Offset(
                    x(maxIdx) - maxLabel.size.width / 2f,
                    y(points[maxIdx].speed.value) - maxLabel.size.height - 4.dp.toPx()
                )
            )

            val s = scrub
            if (s != null) {
                val cx = s * step
                drawLine(
                    color = Color.White.copy(alpha = 0.7f),
                    start = Offset(cx, axisTop),
                    end = Offset(cx, axisTop + plotH),
                    strokeWidth = 1.5.dp.toPx()
                )
                val cy = y(curve.at(s))
                drawCircle(color = Color.Black.copy(alpha = 0.4f), radius = 7.dp.toPx(), center = Offset(cx, cy))
                drawCircle(color = Color.White, radius = 5.dp.toPx(), center = Offset(cx, cy))
            }
        }
        val shownIdx =
            scrub?.roundToInt()
                ?: points.indexOfLast { !it.datetime.isAfter(now) }.coerceAtLeast(0)
        val shown = points.getOrNull(shownIdx)
        if (shown != null) {
            Text(
                text = shown.datetime.format(timeFormatter) +
                    " · " + shown.speed.string() +
                    " · " + shown.speed.bftString(),
                style = MaterialTheme.typography.labelMedium,
                color = onSurfaceVariant,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 6.dp),
                textAlign = androidx.compose.ui.text.style.TextAlign.Center
            )
        }
    }
}
'''
start = s.index("@Composable\nfun WindGraph(")
s = s[:start] + NEW_WIND
ok("WindGraph: modernized (curve, gradient, drag-scrub)")
open(p, "w").write(s)

print()
print("\n".join(log))
