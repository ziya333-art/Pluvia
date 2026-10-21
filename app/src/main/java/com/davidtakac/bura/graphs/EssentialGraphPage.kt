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

package com.davidtakac.bura.graphs
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndex
import com.davidtakac.bura.graphs.uvindex.compose.UvIndexGraph
import com.davidtakac.bura.graphs.uvindex.UvIndexGraph
import com.davidtakac.bura.graphs.wind.compose.WindGraph
import com.davidtakac.bura.graphs.wind.WindGraph
import com.davidtakac.bura.forecast.parameters.wind.WindSpeed

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.ui.Modifier
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.davidtakac.bura.R
import com.davidtakac.bura.common.compose.TextSkeleton
import com.davidtakac.bura.forecast.parameters.precipitation.MixedPrecipitation
import com.davidtakac.bura.forecast.parameters.temperature.Temperature
import com.davidtakac.bura.graphs.common.GraphArgs
import androidx.compose.ui.text.font.FontStyle
import com.davidtakac.bura.common.compose.rememberDateTimeHourMinuteFormatter
import com.davidtakac.bura.forecast.parameters.temperature.string as tempValueString
import com.davidtakac.bura.forecast.parameters.uvindex.valueString as uvValueString
import com.davidtakac.bura.forecast.parameters.wind.valueString as windValueString
import com.davidtakac.bura.graphs.common.compose.GraphScreenSectionLabel
import com.davidtakac.bura.graphs.pop.PopGraph
import com.davidtakac.bura.graphs.pop.compose.PopGraph
import com.davidtakac.bura.graphs.precipitation.PrecipitationGraph
import com.davidtakac.bura.graphs.precipitation.PrecipitationTotal
import com.davidtakac.bura.graphs.precipitation.compose.PrecipitationBullets
import com.davidtakac.bura.graphs.precipitation.compose.PrecipitationGraph
import com.davidtakac.bura.graphs.precipitation.compose.TodayPrecipitationBullets
import com.davidtakac.bura.graphs.temperature.TemperatureGraph
import com.davidtakac.bura.graphs.temperature.TemperatureGraphSummary
import com.davidtakac.bura.graphs.temperature.compose.TemperatureGraph
import com.davidtakac.bura.graphs.temperature.compose.TemperatureGraphSummary
import com.davidtakac.bura.summary.now.compose.NowSummarySkeleton
import java.time.Instant

private const val graphAspectRatio = 4f / 3f
private val verticalSpacing = 24.dp
private val graphLabelSpacing = 8.dp

@Composable
fun EssentialGraphPage(
    listState: LazyListState,
    contentPadding: PaddingValues,
    now: Instant,
    metric: GraphMetric?,
    briefing: DayBriefing?,
    summary: TemperatureGraphSummary,
    temperatureGraph: TemperatureGraph,
    minTemp: Temperature,
    maxTemp: Temperature,
    temperatureArgs: GraphArgs,
    popGraph: PopGraph,
    popArgs: GraphArgs,
    windGraph: WindGraph,
    windMax: WindSpeed,
    uvIndexGraph: UvIndexGraph,
    uvIndexMax: UvIndex,
    precipGraph: PrecipitationGraph,
    precipArgs: GraphArgs,
    precipMax: MixedPrecipitation,
    precipitationTotal: PrecipitationTotal
) {
    LazyColumn(
        state = listState,
        verticalArrangement = Arrangement.spacedBy(verticalSpacing),
        contentPadding = contentPadding,
        modifier = Modifier.fillMaxSize()
    ) {
        if (metric == null || metric == GraphMetric.Temperature) {
            item {
                TemperatureGraphSummary(
                    state = summary,
                    modifier = Modifier.fillMaxWidth()
                )
            }
            item {
                TemperatureGraph(
                    now = now,
                    points = temperatureGraph.points,
                    min = minTemp,
                    max = maxTemp,
                    args = temperatureArgs,
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(graphAspectRatio)
                        .border(
                            width = Dp.Hairline,
                            shape = MaterialTheme.shapes.large,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        .clip(MaterialTheme.shapes.large)
                )
            }
        }
        if (metric == null || metric == GraphMetric.UvIndex) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_uv_index))
                    UvIndexGraph(
                        state = uvIndexGraph,
                        max = uvIndexMax,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
        }
        if (metric == null || metric == GraphMetric.Wind) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_wind))
                    WindGraph(
                        state = windGraph,
                        max = windMax,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
        }
        if (metric == null || metric == GraphMetric.Pop) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_pop))
                    PopGraph(
                        now = now,
                        points = popGraph.points,
                        args = popArgs,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
        }
        if (metric == null || metric == GraphMetric.Precipitation) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_precip))
                    PrecipitationGraph(
                        now = now,
                        points = precipGraph.points,
                        max = precipMax,
                        args = precipArgs,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
            item {
                when (precipitationTotal) {
                    is PrecipitationTotal.OtherDay -> PrecipitationBullets(
                        state = precipitationTotal.total,
                        modifier = Modifier.fillMaxWidth()
                    )

                    is PrecipitationTotal.Today -> TodayPrecipitationBullets(
                        state = precipitationTotal,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
        if (metric != null) {
            item {
                BriefingText(briefing = briefing, metric = metric)
            }
        }
        item {
            Text(
                text = stringResource(id = R.string.credit_weather),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun BriefingText(briefing: DayBriefing?, metric: GraphMetric?) {
    if (briefing == null) return
    val formatter = rememberDateTimeHourMinuteFormatter()
    val text = when (metric) {
        GraphMetric.Temperature -> {
            val max = briefing.tempMax ?: return
            stringResource(
                R.string.briefing_temperature,
                (briefing.tempMin ?: max).tempValueString(),
                max.tempValueString(),
                briefing.tempMaxAt?.let { formatter.format(it.toLocalTime()) } ?: ""
            )
        }
        GraphMetric.Wind -> {
            val wind = briefing.windMax ?: return
            val gust = briefing.gustMax ?: return
            stringResource(
                R.string.briefing_wind,
                wind.windValueString(),
                gust.windValueString(),
                briefing.gustMaxAt?.let { formatter.format(it.toLocalTime()) } ?: ""
            )
        }
        GraphMetric.UvIndex -> {
            val uv = briefing.uvMax ?: return
            stringResource(
                R.string.briefing_uv,
                uv.uvValueString(),
                briefing.uvMaxAt?.let { formatter.format(it.toLocalTime()) } ?: ""
            )
        }
        GraphMetric.Precipitation, GraphMetric.Pop -> {
            val pop = briefing.popMax ?: return
            stringResource(
                R.string.briefing_pop,
                stringResource(R.string.pop_value_percent, pop),
                briefing.popMaxAt?.let { formatter.format(it.toLocalTime()) } ?: ""
            )
        }
        else -> return
    }
    Column(modifier = Modifier.fillMaxWidth()) {
        Text(
            text = stringResource(R.string.briefing_daily_summary),
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier
                .fillMaxWidth()
                .clip(MaterialTheme.shapes.medium)
                .background(MaterialTheme.colorScheme.surfaceContainer)
                .padding(14.dp)
        )
    }
}

@Composable
fun EssentialGraphPageLoadingIndicator(
    shimmerColor: State<Color>,
    contentPadding: PaddingValues,
    modifier: Modifier = Modifier
) {
    LazyColumn(
        modifier = modifier,
        verticalArrangement = Arrangement.spacedBy(verticalSpacing),
        userScrollEnabled = false,
        contentPadding = contentPadding
    ) {
        item {
            NowSummarySkeleton(
                color = shimmerColor,
                modifier = Modifier.fillMaxWidth()
            )
        }
        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(graphAspectRatio)
                    .background(shape = MaterialTheme.shapes.large, color = shimmerColor.value),
            )
        }
        item {
            Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                TextSkeleton(
                    color = shimmerColor,
                    shape = MaterialTheme.shapes.small,
                    style = MaterialTheme.typography.titleSmall,
                    modifier = Modifier.width(160.dp)
                )
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(graphAspectRatio)
                        .background(shape = MaterialTheme.shapes.large, color = shimmerColor.value),
                )
            }
        }
    }
}