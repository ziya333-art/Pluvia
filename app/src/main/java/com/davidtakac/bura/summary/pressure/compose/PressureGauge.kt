/*
 * Pressure gauge adapted from Stratus (https://github.com/Yigder/stratus)
 * Copyright (C) 2026 Yigder, GPL-3.0-or-later. Ported to Pluvia's theme.
 * Pluvia is GPLv3, like Bura; see the LICENSE file.
 */

package com.davidtakac.bura.summary.pressure.compose

import androidx.compose.foundation.Canvas
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import com.davidtakac.bura.R
import com.davidtakac.bura.forecast.parameters.pressure.Pressure
import com.davidtakac.bura.forecast.parameters.pressure.unitString
import com.davidtakac.bura.forecast.parameters.pressure.valueString
import com.davidtakac.bura.summary.pressure.PressureSummary
import com.davidtakac.bura.summary.pressure.PressureTrend
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.sin

@Composable
internal fun PressureGauge(
    state: PressureSummary,
    modifier: Modifier = Modifier
) {
    val ink = MaterialTheme.colorScheme.onSurface
    val muted = MaterialTheme.colorScheme.onSurfaceVariant
    val valueStyle = MaterialTheme.typography.headlineSmall
    val unitStyle = MaterialTheme.typography.labelSmall
    val trendStyle = MaterialTheme.typography.labelMedium
    val endStyle = MaterialTheme.typography.labelSmall
    val measurer = rememberTextMeasurer()
    val hpa = state.now.convertTo(Pressure.Unit.Hectopascal).value
    val valueText = state.now.valueString()
    val unitText = state.now.unitString()
    val lowLabel = stringResource(R.string.pressure_gauge_low)
    val highLabel = stringResource(R.string.pressure_gauge_high)
    Canvas(modifier = modifier) {
        val r = size.minDimension / 2 * 0.95f
        val c = center
        val startDeg = 135f
        val sweep = 270f
        val ticks = 48
        val frac = (((hpa - 960) / 100.0)).coerceIn(0.0, 1.0).toFloat()
        for (i in 0..ticks) {
            val a = Math.toRadians((startDeg + sweep * i / ticks).toDouble())
            val f = i / ticks.toFloat()
            val near = abs(f - frac) < 0.012f
            drawLine(
                (if (near) ink else muted).copy(alpha = if (near) 1f else 0.35f),
                Offset(c.x + cos(a).toFloat() * r * 0.80f, c.y + sin(a).toFloat() * r * 0.80f),
                Offset(
                    c.x + cos(a).toFloat() * r * (if (near) 1.02f else 0.98f),
                    c.y + sin(a).toFloat() * r * (if (near) 1.02f else 0.98f)
                ),
                strokeWidth = (if (near) 3.5f else 1.4f) * density,
                cap = StrokeCap.Round
            )
        }
        val label = measurer.measure(valueText, valueStyle.copy(color = ink))
        drawText(label, topLeft = Offset(c.x - label.size.width / 2, c.y - label.size.height / 2 + 4 * density))
        val unit = measurer.measure(unitText, unitStyle.copy(color = muted))
        drawText(unit, topLeft = Offset(c.x - unit.size.width / 2, c.y + label.size.height / 2 + 2 * density))
        val ly = c.y - label.size.height / 2 - 12 * density
        val tl = measurer.measure(
            when (state.trend) {
                PressureTrend.Rising -> "↑"
                PressureTrend.Falling -> "↓"
                else -> "="
            },
            trendStyle.copy(color = muted)
        )
        drawText(tl, topLeft = Offset(c.x - tl.size.width / 2, ly - tl.size.height / 2))
        val low = measurer.measure(lowLabel, endStyle.copy(color = muted))
        val high = measurer.measure(highLabel, endStyle.copy(color = muted))
        drawText(low, topLeft = Offset(c.x - r * 0.62f - low.size.width / 2, c.y + r * 0.72f))
        drawText(high, topLeft = Offset(c.x + r * 0.62f - high.size.width / 2, c.y + r * 0.72f))
    }
}
