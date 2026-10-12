package com.davidtakac.bura.summary.wind.compose

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.text.drawText
import androidx.compose.ui.text.rememberTextMeasurer
import androidx.compose.ui.unit.dp
import kotlin.math.cos
import kotlin.math.sin

@Composable
internal fun WindCompass(
    directionDegrees: Double,
    speed: String,
    unit: String,
    modifier: Modifier = Modifier
) {
    val ink = MaterialTheme.colorScheme.onSurface
    val muted = MaterialTheme.colorScheme.onSurfaceVariant
    val speedStyle = MaterialTheme.typography.headlineSmall
    val unitStyle = MaterialTheme.typography.labelSmall
    val cardinalStyle = MaterialTheme.typography.labelMedium
    val measurer = rememberTextMeasurer()
    Canvas(modifier = modifier.size(132.dp)) {
        val r = size.minDimension / 2
        val c = center
        for (i in 0 until 180) {
            val a = Math.toRadians(i * 2.0 - 90)
            val major = i % 15 == 0
            val len = if (major) 0.12f else 0.07f
            drawLine(
                color = (if (major) ink else muted).copy(alpha = if (major) 0.75f else 0.3f),
                start = Offset(c.x + cos(a).toFloat() * r * (1 - len), c.y + sin(a).toFloat() * r * (1 - len)),
                end = Offset(c.x + cos(a).toFloat() * r, c.y + sin(a).toFloat() * r),
                strokeWidth = (if (major) 1.6f else 0.9f) * density,
                cap = StrokeCap.Round
            )
        }
        listOf("N" to 0.0, "E" to 90.0, "S" to 180.0, "W" to 270.0).forEach { (t, deg) ->
            val label = measurer.measure(t, cardinalStyle.copy(color = if (t == "N") ink else muted))
            val a = Math.toRadians(deg - 90)
            val rr = r * 0.66f
            drawText(
                label,
                topLeft = Offset(
                    x = c.x + cos(a).toFloat() * rr - label.size.width / 2,
                    y = c.y + sin(a).toFloat() * rr - label.size.height / 2
                )
            )
        }
        rotate(degrees = directionDegrees.toFloat() + 180f, pivot = c) {
            val tip = Offset(c.x, c.y - r * 0.92f)
            val tail = Offset(c.x, c.y + r * 0.92f)
            val gap = r * 0.36f
            drawLine(ink, Offset(c.x, c.y - gap), Offset(c.x, tip.y + 8 * density), 3f * density, StrokeCap.Round)
            drawLine(ink, Offset(c.x, c.y + gap), Offset(c.x, tail.y - 4 * density), 3f * density, StrokeCap.Round)
            val head = Path().apply {
                moveTo(tip.x, tip.y)
                lineTo(tip.x - 6 * density, tip.y + 11 * density)
                lineTo(tip.x + 6 * density, tip.y + 11 * density)
                close()
            }
            drawPath(head, ink)
            drawCircle(ink, 4 * density, tail, style = Stroke(2.5f * density))
        }
        val sp = measurer.measure(speed, speedStyle.copy(color = ink))
        val un = measurer.measure(unit, unitStyle.copy(color = muted))
        drawText(sp, topLeft = Offset(c.x - sp.size.width / 2, c.y - sp.size.height / 2 - 5 * density))
        drawText(un, topLeft = Offset(c.x - un.size.width / 2, c.y - un.size.height / 2 + 18 * density))
    }
}
