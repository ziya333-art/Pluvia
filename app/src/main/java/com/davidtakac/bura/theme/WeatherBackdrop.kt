package com.davidtakac.bura.theme

import androidx.compose.ui.graphics.Color
import com.davidtakac.bura.R
import com.davidtakac.bura.forecast.parameters.condition.Condition

data class SkyBackdrop(val imageRes: Int, val glass: Color)

fun weatherBackdrop(condition: Condition, hour: Int): SkyBackdrop {
    if (hour in 5..8 || hour in 17..20) {
        if (condition.wmoCode in 0..3) {
            return SkyBackdrop(R.drawable.sky_sunset, Color(0xFF696969))
        }
    }
    return when (condition.wmoCode) {
        in 0..1 -> if (condition.isDay) SkyBackdrop(R.drawable.sky_sunny, Color(0xFF8A6A5C))
                   else SkyBackdrop(R.drawable.sky_night, Color(0xFF7A8C7A))
        2 -> SkyBackdrop(R.drawable.sky_partly_cloudy, Color(0xFFB0AC98))
        3 -> SkyBackdrop(R.drawable.sky_cloudy, Color(0xFFA68A5F))
        45, 48 -> SkyBackdrop(R.drawable.sky_fog, Color(0xFF8A6666))
        in 51..67, in 80..82 -> SkyBackdrop(R.drawable.sky_rain, Color(0xFF6B4C63))
        in 71..77, 85, 86 -> SkyBackdrop(R.drawable.sky_snow, Color(0xFF7E8C7B))
        in 95..99 -> SkyBackdrop(R.drawable.sky_storm, Color(0xFF5F6757))
        else -> SkyBackdrop(R.drawable.sky_cloudy, Color(0xFFA68A5F))
    }
}
