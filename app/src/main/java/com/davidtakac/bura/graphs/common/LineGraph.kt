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

package com.davidtakac.bura.graphs.common

import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import com.davidtakac.bura.graphs.common.drawing.closePlotFillPath
import com.davidtakac.bura.graphs.common.drawing.drawGutterIcon
import com.davidtakac.bura.graphs.common.drawing.drawLabeledPoint
import com.davidtakac.bura.graphs.common.drawing.drawMeasuredTickLabel
import com.davidtakac.bura.graphs.common.drawing.drawPastOverlayWithPoint
import com.davidtakac.bura.graphs.common.drawing.drawPlotLinePath
import com.davidtakac.bura.graphs.common.drawing.drawTimeAxis
import com.davidtakac.bura.graphs.common.drawing.drawVerticalAxis
import java.time.Instant
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit

@Composable
fun LineGraph(
    plotPoints: List<PlotPoint>,
    plotBrush: Brush,
    gutterIcons: List<ImageBitmap>,
    valueTicks: List<ValueTick>,
    valueFormatter: (Double) -> String,
    now: Instant,
    args: GraphArgs,
    modifier: Modifier = Modifier,
    plotUnderfillBrush: Brush? = null,
) {
    var scrub by remember(plotPoints) { mutableStateOf<Float?>(null) }
    val curve = remember(plotPoints) { Curve(plotPoints.map { it.value }) }
    val scrubTimes = remember(plotPoints) { plotPoints.map { it.time } }
    Canvas(
        modifier.scrubGesture { x, w ->
            scrub = x?.let { px -> mapScrubPosition(px, w, scrubTimes, args) }
        }
    ) {
        val verticalAxisDrawLater = drawVerticalAxis(
            valueTicks = valueTicks,
            args = args,
            valueFormatter = valueFormatter
        )
        val horizontalAxisDrawLater = drawHorizontalAxisAndPlot(
            plotPoints = plotPoints,
            plotBrush = plotBrush,
            plotUnderfillBrush = plotUnderfillBrush,
            gutterIcons = gutterIcons,
            valueFormatter = valueFormatter,
            curve = curve,
            scrub = scrub,
            min = valueTicks.minOf { it.value },
            max = valueTicks.maxOf { it.value },
            now = now,
            args = args
        )
        verticalAxisDrawLater.measuredTickLabels.forEach {
            drawMeasuredTickLabel(args, it)
        }
        horizontalAxisDrawLater.nowCenter?.let {
            drawPastOverlayWithPoint(it, args)
        }
    }
}

private fun DrawScope.drawHorizontalAxisAndPlot(
    plotPoints: List<PlotPoint>,
    curve: Curve,
    scrub: Float?,
    plotBrush: Brush,
    plotUnderfillBrush: Brush?,
    gutterIcons: List<ImageBitmap>,
    valueFormatter: (Double) -> String,
    min: Double,
    max: Double,
    now: Instant,
    args: GraphArgs
): HorizontalAxisDrawLater {
    val range = max - min
    val plotPath = Path()
    val plotFillPath = Path()
    val plotXs = mutableListOf<Float>()
    val plotYs = mutableListOf<Float>()
    fun movePlot(x: Float, y: Float) {
        plotXs.add(x)
        plotYs.add(y)
    }

    var minCenter: Pair<Offset, Double>? = null
    var maxCenter: Pair<Offset, Double>? = null
    var nowCenter: Offset? = null
    var lastX = 0f

    drawTimeAxis(
        times = plotPoints.map { it.time },
        args = args
    ) { i, x, calcY ->
        // Temperature line
        val point = plotPoints.getOrNull(i) ?: return@drawTimeAxis
        val y = calcY((point.value - min) / range).top
        movePlot(x, y)
        lastX = x

        // Min, max and now indicators are drawn after the plot so they're on top of it
        if (point.value < (minCenter?.second ?: Double.MAX_VALUE)) minCenter = Offset(x, y) to point.value
        if (point.value > (maxCenter?.second ?: Double.MIN_VALUE)) maxCenter = Offset(x, y) to point.value
        if (point.time.toInstant() == now.truncatedTo(ChronoUnit.HOURS)) nowCenter = Offset(x, y)

        // Condition icons
        drawGutterIcon(i, x, gutterIcons[i], args)
    }

    if (plotXs.size >= 2) {
        curve.trace(
            xs = plotXs,
            ys = plotYs,
            path = plotPath,
            area = plotFillPath,
            baseY = size.height - args.bottomGutter
        )
    }

    drawPlotLinePath(lastX, args) {
        drawPath(
            plotPath,
            brush = plotBrush,
            style = Stroke(
                width = args.plotWidth,
                join = StrokeJoin.Round,
                cap = StrokeCap.Round
            )
        )
    }

    plotUnderfillBrush?.let {
        drawPath(
            plotFillPath,
            brush = it
        )
    }

    minCenter?.let { (offset, value) ->
        drawLabeledPoint(
            label = valueFormatter(value),
            center = offset,
            args = args,
        )
    }
    maxCenter?.let { (offset, value) ->
        drawLabeledPoint(
            label = valueFormatter(value),
            center = offset,
            args = args,
        )
    }

    scrub?.let { sPos ->
        if (plotXs.size >= 2) {
            val i0 = sPos.toInt().coerceIn(0, plotXs.size - 1)
            val i1 = (i0 + 1).coerceAtMost(plotXs.size - 1)
            val frac = (sPos - i0).coerceIn(0f, 1f)
            val cx = plotXs[i0] + (plotXs[i1] - plotXs[i0]) * frac
            val v = curve.at(sPos)
            val percent = ((v - min) / range).toFloat()
            val plotHeight = size.height - args.topGutter - args.bottomGutter
            val cy = ((1 - percent) * plotHeight) + args.topGutter
            drawLine(
                color = args.axisColor,
                start = Offset(cx, args.topGutter),
                end = Offset(cx, size.height - args.bottomGutter),
                strokeWidth = args.axisWidth * 2
            )
            drawCircle(args.pointOutlineColor, args.pointCenterRadius * 2.5f, Offset(cx, cy))
            drawLabeledPoint(
                label = valueFormatter(v),
                center = Offset(cx, cy),
                args = args,
            )
        }
    }

    return HorizontalAxisDrawLater(nowCenter)
}

data class PlotPoint(
    val value: Double,
    val time: ZonedDateTime,
)

data class ValueTick(
    val value: Double,
    val label: String? = null,
)
private fun mapScrubPosition(
    px: Float,
    width: Float,
    times: List<ZonedDateTime>,
    args: GraphArgs
): Float? {
    val plotW = width - args.endGutter - args.startGutter
    if (plotW <= 0f || times.size < 2) return null
    val pct = ((px - args.startGutter) / plotW).coerceIn(0f, 1f)
    val t0 = times.first().toInstant()
    val total = ChronoUnit.SECONDS.between(t0, times.last().toInstant())
    val tSec = (pct * total).toLong()
    for (i in 0 until times.size - 1) {
        val s0 = ChronoUnit.SECONDS.between(t0, times[i].toInstant())
        val s1 = ChronoUnit.SECONDS.between(t0, times[i + 1].toInstant())
        if (tSec <= s1) {
            return (if (s1 > s0) i + (tSec - s0).toFloat() / (s1 - s0) else i.toFloat())
                .coerceIn(0f, (times.size - 1).toFloat())
        }
    }
    return (times.size - 1).toFloat()
}
