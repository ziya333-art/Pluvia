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

package com.davidtakac.bura.graphs.wind

import com.davidtakac.bura.forecast.parameters.wind.WindDirection
import com.davidtakac.bura.forecast.parameters.wind.WindMoment
import com.davidtakac.bura.forecast.parameters.wind.WindPeriod
import com.davidtakac.bura.forecast.parameters.wind.WindSpeed
import java.time.LocalDate
import java.time.ZonedDateTime

fun getWindGraphs(now: ZonedDateTime, windPeriod: WindPeriod): WindGraphs? {
    val windDays = windPeriod.dayMomentsFrom(now.toLocalDate()) ?: return null
    val windGraphPeriods = windDays.map { WindPeriod(it) }
    return WindGraphs(
        max = windPeriod.maximumSpeed,
        graphs = windGraphPeriods.mapIndexed { idx, windDay ->
            getWindGraph(windDay, windGraphPeriods.getOrNull(idx + 1))
        }
    )
}

private fun getWindGraph(windDay: WindPeriod, windTomorrow: WindPeriod?): WindGraph {
    val adjusted =
        if (windTomorrow != null) WindPeriod(windDay + windTomorrow.first())
        else windDay
    return WindGraph(
        day = windDay.first().timeZdt.toLocalDate(),
        points = adjusted.map { moment ->
            WindGraphPoint(
                datetime = moment.timeZdt,
                speed = moment.wind.speed,
                from = moment.wind.from
            )
        }
    )
}

data class WindGraphs(val graphs: List<WindGraph>, val max: WindSpeed)
data class WindGraph(val day: LocalDate, val points: List<WindGraphPoint>)
data class WindGraphPoint(
    val datetime: ZonedDateTime,
    val speed: WindSpeed,
    val from: WindDirection
)
