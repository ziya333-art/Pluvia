/*
 * Copyright 2024 David Takač
 *
 * This file is part of Bura.
 *
 * Bura is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 *
 * Bura is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with Bura. If not, see <https://www.gnu.org/licenses/>.
 */

package com.davidtakac.bura.graphs.wind.compose
import com.davidtakac.bura.forecast.parameters.wind.string
import com.davidtakac.bura.forecast.parameters.wind.bftString

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.davidtakac.bura.graphs.common.GraphArgs
import com.davidtakac.bura.graphs.wind.WindGraph
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.geometry.Size
import com.davidtakac.bura.graphs.common.Curve
import com.davidtakac.bura.graphs.common.scrubGesture
import com.davidtakac.bura.forecast.parameters.wind.WindSpeed
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import kotlin.math.roundToInt

@Composable
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
    val maxLabelText = points[maxIdx].speed.string()
    var scrub by remember(state) { mutableStateOf<Float?>(null) }

    Column(modifier = modifier.padding(10.dp)) {
        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .scrubGesture { x, w ->
                    scrub = x?.let { px ->
                        val step = if (points.size > 1) w / (points.size - 1) else w
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
                maxLabelText,
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
