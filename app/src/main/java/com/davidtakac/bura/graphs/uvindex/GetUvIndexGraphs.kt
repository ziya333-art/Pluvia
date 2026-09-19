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

package com.davidtakac.bura.graphs.uvindex

import com.davidtakac.bura.forecast.HourPeriod
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndexMoment
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndexPeriod
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndex
import java.time.LocalDate
import java.time.LocalDateTime

fun getUvIndexGraphs(now: LocalDateTime, uvIndexPeriod: UvIndexPeriod): UvIndexGraphs? {
    val uvDays = uvIndexPeriod.daysFrom(now.toLocalDate()) ?: return null
    return UvIndexGraphs(
        max = uvIndexPeriod.maximum,
        graphs = uvDays.mapIndexed { idx, uvDay ->
            getUvIndexGraph(uvDay, uvDays.getOrNull(idx + 1))
        }
    )
}

private fun getUvIndexGraph(uvDay: HourPeriod<UvIndexMoment>, uvTomorrow: HourPeriod<UvIndexMoment>?): UvIndexGraph {
    val adjusted =
        if (uvTomorrow != null) UvIndexPeriod(uvDay + uvTomorrow.first())
        else uvDay
    return UvIndexGraph(
        day = uvDay.first().hour.toLocalDate(),
        points = adjusted.map { moment ->
            UvIndexGraphPoint(
                datetime = moment.hour,
                uvIndex = moment.uvIndex,
            )
        }
    )
}

data class UvIndexGraphs(val graphs: List<UvIndexGraph>, val max: UvIndex)
data class UvIndexGraph(val day: LocalDate, val points: List<UvIndexGraphPoint>)
data class UvIndexGraphPoint(
    val datetime: LocalDateTime,
    val uvIndex: UvIndex,
)
