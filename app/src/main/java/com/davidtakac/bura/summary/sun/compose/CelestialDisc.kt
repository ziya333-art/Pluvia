package com.davidtakac.bura.summary.sun.compose

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.BlendMode
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import kotlin.math.cos
import kotlin.math.sin

@Composable
internal fun CelestialDisc(
    isDay: Boolean,
    modifier: Modifier = Modifier
) {
    val ink = Color(0xFFF5F2E8)
    val accent = Color(0xFFF6C445)
    Canvas(modifier = modifier.size(96.dp)) {
        val c = center
        val r = size.minDimension * 0.28f
        if (isDay) {
            drawCircle(accent.copy(alpha = 0.9f), r, c)
            for (i in 0 until 12) {
                val a = Math.toRadians(i * 30.0)
                val inner = r * 1.35f
                val outer = r * 1.8f
                drawLine(
                    color = accent.copy(alpha = 0.7f),
                    start = Offset(c.x + cos(a).toFloat() * inner, c.y + sin(a).toFloat() * inner),
                    end = Offset(c.x + cos(a).toFloat() * outer, c.y + sin(a).toFloat() * outer),
                    strokeWidth = 2.5f * density
                )
            }
        } else {
            drawCircle(ink, r, c)
            drawCircle(
                color = Color.Black,
                radius = r * 0.85f,
                center = Offset(c.x + r * 0.5f, c.y - r * 0.35f),
                blendMode = BlendMode.Clear
            )
            for (i in 0 until 8) {
                val a = Math.toRadians(i * 45.0 + 22.0)
                val rr = r * 2.1f
                drawCircle(
                    ink.copy(alpha = 0.6f),
                    2.2f * density,
                    Offset(c.x + cos(a).toFloat() * rr, c.y + sin(a).toFloat() * rr)
                )
            }
        }
    }
}
