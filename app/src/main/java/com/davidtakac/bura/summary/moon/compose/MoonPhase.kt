package com.davidtakac.bura.summary.moon.compose

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.davidtakac.bura.R
import com.davidtakac.bura.common.compose.rememberNumberFormat
import com.davidtakac.bura.summary.common.compose.SummaryTile
import java.time.Duration
import java.time.Instant
import java.time.ZonedDateTime
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.roundToInt

private const val SYNODIC = 29.530588853
private val REF_NEW_MOON: Instant = Instant.parse("2000-01-06T18:14:00Z")
private val MoonLit = Color(0xFFF5F2E8)
private val MoonDark = Color(0xFF39414F)

private fun moonAge(now: Instant): Double {
    val days = Duration.between(REF_NEW_MOON, now).seconds / 86400.0
    return ((days % SYNODIC) + SYNODIC) % SYNODIC
}

private fun moonIllumination(now: Instant): Double =
    (1 - cos(2 * Math.PI * moonAge(now) / SYNODIC)) / 2

private fun moonPhaseNameRes(f: Double): Int = when {
    f < 0.0339 || f > 0.9661 -> R.string.moon_new
    f < 0.2161 -> R.string.moon_waxing_crescent
    f < 0.2839 -> R.string.moon_first_quarter
    f < 0.4661 -> R.string.moon_waxing_gibbous
    f < 0.5339 -> R.string.moon_full
    f < 0.7161 -> R.string.moon_waning_gibbous
    f < 0.7839 -> R.string.moon_last_quarter
    else -> R.string.moon_waning_crescent
}

@Composable
internal fun MoonDisc(
    phaseFraction: Double,
    illumination: Double,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier.size(96.dp)) {
        val r = size.minDimension / 2
        val c = center
        val waxing = phaseFraction < 0.5
        val litStart = if (waxing) -90f else 90f
        drawCircle(MoonDark, r, c)
        drawArc(MoonLit, litStart, 180f, true, Offset(c.x - r, c.y - r), Size(2f * r, 2f * r))
        val k = (2f * illumination.toFloat()) - 1f
        val rx = r * abs(k)
        val terminator = if (k < 0f) MoonDark else MoonLit
        drawArc(terminator, litStart, 180f, true, Offset(c.x - rx, c.y - r), Size(2f * rx, 2f * r))
    }
}

@Composable
fun MoonPhase(modifier: Modifier = Modifier) {
    val now = remember { ZonedDateTime.now().toInstant() }
    val f = moonAge(now) / SYNODIC
    val illum = moonIllumination(now)
    val numberFormat = rememberNumberFormat()
    SummaryTile(
        label = { Text(stringResource(R.string.moon)) },
        value = { MoonDisc(phaseFraction = f, illumination = illum) },
        supportingValue = { Text(stringResource(moonPhaseNameRes(f))) },
        bottom = {
            Text(stringResource(R.string.moon_illumination, numberFormat.format((illum * 100).roundToInt())))
        },
        modifier = modifier
    )
}
