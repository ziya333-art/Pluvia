package com.davidtakac.bura.graphs

import com.davidtakac.bura.forecast.parameters.gust.GustPeriod
import com.davidtakac.bura.forecast.parameters.pop.PopPeriod
import com.davidtakac.bura.forecast.parameters.temperature.Temperature
import com.davidtakac.bura.forecast.parameters.temperature.TemperaturePeriod
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndex
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndexPeriod
import com.davidtakac.bura.forecast.parameters.wind.WindPeriod
import com.davidtakac.bura.forecast.parameters.wind.WindSpeed
import java.time.LocalDate
import java.time.ZonedDateTime

data class DayBriefing(
    val tempMin: Temperature?,
    val tempMax: Temperature?,
    val tempMaxAt: ZonedDateTime?,
    val gustMax: WindSpeed?,
    val gustMaxAt: ZonedDateTime?,
    val windMax: WindSpeed?,
    val windMaxAt: ZonedDateTime?,
    val uvMax: UvIndex?,
    val uvMaxAt: ZonedDateTime?,
    val popMax: Int?,
    val popMaxAt: ZonedDateTime?
)

fun getDayBriefing(
    day: LocalDate,
    temperaturePeriod: TemperaturePeriod,
    gustPeriod: GustPeriod,
    windPeriod: WindPeriod,
    uvIndexPeriod: UvIndexPeriod,
    popPeriod: PopPeriod
): DayBriefing {
    val temps = temperaturePeriod.dayMomentsOn(day)
    val gusts = gustPeriod.dayMomentsOn(day)
    val uvs = uvIndexPeriod.dayMomentsOn(day)
    val pops = popPeriod.dayMomentsOn(day)
    val tempMaxMoment = temps?.maxByOrNull { it.temperature.value }
    val tempMinMoment = temps?.minByOrNull { it.temperature.value }
    val gustMoment = gusts?.maxByOrNull { it.speed.value }
    val winds = windPeriod.dayMomentsOn(day)
    val windMoment = winds?.maxByOrNull { it.wind.speed.value }
    val uvMoment = uvs?.maxByOrNull { it.uvIndex.value }
    val popMoment = pops?.maxByOrNull { it.pop.value }
    return DayBriefing(
        tempMin = tempMinMoment?.temperature,
        tempMax = tempMaxMoment?.temperature,
        tempMaxAt = tempMaxMoment?.timeZdt,
        gustMax = gustMoment?.speed,
        gustMaxAt = gustMoment?.timeZdt,
        windMax = windMoment?.wind?.speed,
        windMaxAt = windMoment?.timeZdt,
        uvMax = uvMoment?.uvIndex,
        uvMaxAt = uvMoment?.timeZdt,
        popMax = popMoment?.pop?.value,
        popMaxAt = popMoment?.timeZdt
    )
}
