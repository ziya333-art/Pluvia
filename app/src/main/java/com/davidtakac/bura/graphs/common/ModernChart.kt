/*
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
        if (values.size >= 2) {
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
 * scroll view. Reports the finger's x and the element width, then null on release.
 */
fun Modifier.scrubGesture(onScrub: (x: Float?, width: Float) -> Unit): Modifier = pointerInput(Unit) {
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
        onScrub(x, size.width.toFloat())
        while (true) {
            val c = awaitPointerEvent().changes.firstOrNull { it.id == down.id } ?: break
            if (!c.pressed) break
            c.consume()
            onScrub(c.position.x, size.width.toFloat())
        }
        onScrub(null, size.width.toFloat())
    }
}
