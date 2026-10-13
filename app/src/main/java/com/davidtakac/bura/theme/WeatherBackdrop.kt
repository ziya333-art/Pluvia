package com.davidtakac.bura.theme

import com.davidtakac.bura.R
import com.davidtakac.bura.forecast.parameters.condition.Condition

fun weatherBackdropRes(condition: Condition, hour: Int): Int {
    if (hour in 5..8 || hour in 17..20) {
        if (condition.wmoCode in 0..3) return R.drawable.sky_sunset
    }
    return when (condition.wmoCode) {
        in 0..1 -> if (condition.isDay) R.drawable.sky_sunny else R.drawable.sky_night
        2 -> R.drawable.sky_partly_cloudy
        3 -> R.drawable.sky_cloudy
        45, 48 -> R.drawable.sky_fog
        in 51..67, in 80..82 -> R.drawable.sky_rain
        in 71..77, 85, 86 -> R.drawable.sky_snow
        in 95..99 -> R.drawable.sky_storm
        else -> R.drawable.sky_cloudy
    }
}
