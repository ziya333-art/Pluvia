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

package com.davidtakac.bura.summary.pressure.compose

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.text.InlineTextContent
import androidx.compose.foundation.text.appendInlineContent
import androidx.compose.material3.Icon
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.Placeholder
import androidx.compose.ui.text.PlaceholderVerticalAlign
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.davidtakac.bura.R
import com.davidtakac.bura.forecast.parameters.pressure.Pressure
import com.davidtakac.bura.forecast.parameters.pressure.image
import com.davidtakac.bura.forecast.parameters.pressure.string
import com.davidtakac.bura.forecast.parameters.pressure.unitString
import com.davidtakac.bura.forecast.parameters.pressure.valueString
import com.davidtakac.bura.summary.common.compose.SummaryTile
import com.davidtakac.bura.summary.common.compose.ValueAndUnit
import com.davidtakac.bura.summary.pressure.PressureSummary
import com.davidtakac.bura.summary.pressure.PressureTrend

@Composable
fun PressureSummary(state: PressureSummary, modifier: Modifier = Modifier) {
    SummaryTile(
        label = { Text(stringResource(R.string.pressure)) },
        value = {
            PressureGauge(
                state = state,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f, matchHeightConstraintsFirst = true)
            )
        },
        bottom = { Text(stringResource(R.string.pressure_value_average, state.average.string())) },
        modifier = modifier
    )
}

@Preview
@Composable
private fun PressureSummaryPreview() {
    MaterialTheme {
        Column(
            modifier = Modifier
                .background(MaterialTheme.colorScheme.background)
                .padding(16.dp)
                .size(200.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            PressureSummary(
                state = PressureSummary(
                    now = Pressure(1013.25, Pressure.Unit.Hectopascal),
                    average = Pressure(1010.0, Pressure.Unit.Hectopascal),
                    trend = PressureTrend.Rising
                )
            )
        }
    }
}