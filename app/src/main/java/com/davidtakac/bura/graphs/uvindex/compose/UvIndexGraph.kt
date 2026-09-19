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

package com.davidtakac.bura.graphs.uvindex.compose
import com.davidtakac.bura.forecast.parameters.uvindex.valueString
import com.davidtakac.bura.forecast.parameters.uvindex.riskString

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
import com.davidtakac.bura.graphs.uvindex.UvIndexGraph
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndex
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import kotlin.math.roundToInt

@Composable
fun UvIndexGraph(
    state: UvIndexGraph,
    max: UvIndex,


    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
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
    val now = remember { LocalDateTime.now() }
    val primary = MaterialTheme.colorScheme.primary
    val onSurfaceVariant = MaterialTheme.colorScheme.onSurfaceVariant
    val timeFormatter = remember { DateTimeFormatter.ofPattern("HH:mm") }
    val measurer = rememberTextMeasurer()
    val linePath = remember { Path() }
    val fillPath = remember { Path() }
    var selectedIndex by remember(state) { mutableStateOf(-1) }
    val maxIdx = points.indices.maxByOrNull { points[it].uvIndex.value } ?: 0
    val maxLabelText = points[maxIdx].uvIndex.valueString()

    Column(modifier = modifier.padding(10.dp)) {
        Canvas(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .pointerInput(points) {
                    detectTapGestures { offset ->
                        val usable = size.width.toFloat()
                        val step =
                            if (points.size > 1) usable / (points.size - 1) else usable
                        selectedIndex =
                            ((offset.x / step).roundToInt()).coerceIn(0, points.lastIndex)
                    }
                }
        ) {
            val axisTop = 16.dp.toPx()
            val axisBottom = 18.dp.toPx()
            val plotH = size.height - axisTop - axisBottom
            if (plotH <= 0f) return@Canvas
            val maxVal = max.value.takeIf { it > 0.0 } ?: 1.0
            val step =
                if (points.size > 1) size.width / (points.size - 1) else 0f
            fun x(i: Int) = i * step
            fun y(uvIndex: UvIndex) = axisTop + plotH - (uvIndex.value / maxVal * plotH).toFloat()

            linePath.reset()
            fillPath.reset()
            points.forEachIndexed { i, p ->
                val px = x(i)
                val py = y(p.uvIndex)
                if (i == 0) linePath.moveTo(px, py) else linePath.lineTo(px, py)
            }
            fillPath.addPath(linePath)
            fillPath.lineTo(x(points.lastIndex), axisTop + plotH)
            fillPath.lineTo(x(0), axisTop + plotH)
            fillPath.close()
            drawPath(fillPath, color = primary.copy(alpha = 0.15f))
            drawPath(linePath, color = primary, style = Stroke(width = 2.dp.toPx()))

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
                    color = androidx.compose.ui.graphics.Color.Black.copy(alpha = 0.05f),
                    topLeft = Offset(0f, axisTop),
                    size = androidx.compose.ui.geometry.Size(nx, plotH)
                )
            }
            points.forEachIndexed { i, p ->
                drawCircle(color = primary, radius = 2.5.dp.toPx(), center = Offset(x(i), y(p.uvIndex)))
                if (p.datetime.hour % 6 == 0) {
                    drawText(
                        textMeasurer = measurer,
                        text = p.datetime.format(timeFormatter),
                        topLeft = Offset(x(i) - 15.dp.toPx(), size.height - axisBottom + 2.dp.toPx()),
                        style = TextStyle(fontSize = 9.sp, color = onSurfaceVariant)
                    )
                }
            }
            val maxIdx = points.indices.maxByOrNull { points[it].uvIndex.value } ?: 0
            val maxLabel = measurer.measure(
                maxLabelText,
                TextStyle(fontSize = 10.sp, color = onSurfaceVariant)
            )
            drawText(
                textLayoutResult = maxLabel,
                topLeft = Offset(
                    x(maxIdx) - maxLabel.size.width / 2f,
                    y(points[maxIdx].uvIndex) - maxLabel.size.height - 4.dp.toPx()
                )
            )
        }
        val shownIdx =
            if (selectedIndex >= 0) selectedIndex
            else points.indexOfLast { !it.datetime.isAfter(now) }.coerceAtLeast(0)
        val shown = points[shownIdx]
        Text(
            text = shown.datetime.format(timeFormatter) +
                " · " + shown.uvIndex.valueString() +
                " · " + shown.uvIndex.riskString(),
            style = MaterialTheme.typography.labelMedium,
            color = onSurfaceVariant,
            modifier = Modifier
                .fillMaxWidth()
                .padding(top = 6.dp),
            textAlign = androidx.compose.ui.text.style.TextAlign.Center
        )
    }
}
