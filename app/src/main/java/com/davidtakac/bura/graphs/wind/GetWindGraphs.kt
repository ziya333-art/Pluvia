package com.davidtakac.bura.graphs.wind

import com.davidtakac.bura.forecast.parameters.wind.WindDirection
import com.davidtakac.bura.forecast.HourPeriod
import com.davidtakac.bura.forecast.parameters.wind.WindMoment
import com.davidtakac.bura.forecast.parameters.wind.WindPeriod
import com.davidtakac.bura.forecast.parameters.wind.WindSpeed
import java.time.LocalDate
import java.time.LocalDateTime

fun getWindGraphs(now: LocalDateTime, windPeriod: WindPeriod): WindGraphs? {
    val windDays = windPeriod.daysFrom(now.toLocalDate()) ?: return null
    return WindGraphs(
        max = windPeriod.maximumSpeed,
        graphs = windDays.mapIndexed { idx, windDay ->
            getWindGraph(windDay, windDays.getOrNull(idx + 1))
        }
    )
}

private fun getWindGraph(windDay: HourPeriod<WindMoment>, windTomorrow: HourPeriod<WindMoment>?): WindGraph {
    val adjusted =
        if (windTomorrow != null) WindPeriod(windDay + windTomorrow.first())
        else windDay
    return WindGraph(
        day = windDay.first().hour.toLocalDate(),
        points = adjusted.map { moment ->
            WindGraphPoint(
                datetime = moment.hour,
                speed = moment.wind.speed,
                from = moment.wind.from
            )
        }
    )
}

data class WindGraphs(val graphs: List<WindGraph>, val max: WindSpeed)
data class WindGraph(val day: LocalDate, val points: List<WindGraphPoint>)
data class WindGraphPoint(
    val datetime: LocalDateTime,
    val speed: WindSpeed,
    val from: WindDirection
)
