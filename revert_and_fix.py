log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- A. Revert the rooms' front-tile headers (keep doors + sky) ----------
# A1. ViewModel: out with the summary lists, keep the backdrop
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsViewModel.kt"
s = open(p).read()
s2 = s.replace(
    "import com.davidtakac.bura.theme.weatherBackdrop\n"
    "import com.davidtakac.bura.summary.wind.getWindSummary\n"
    "import com.davidtakac.bura.summary.wind.WindSummary\n"
    "import com.davidtakac.bura.summary.uvindex.getUvIndexSummary\n"
    "import com.davidtakac.bura.summary.uvindex.UvIndexSummary\n"
    "import java.time.LocalDate\n"
    "import java.time.ZonedDateTime",
    "import com.davidtakac.bura.theme.weatherBackdrop")
if s2 != s: ok("VM: imports reverted"); s = s2
else: warn("VM: import block not found")

s2 = s.replace(
    "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n"
    "        fun summaryTimeFor(day: LocalDate): ZonedDateTime =\n"
    "            if (day == now.toLocalDate()) now else day.atTime(12, 0).atZone(now.zone)\n"
    "        val windSummaries = tempGraphSummaries.map { getWindSummary(summaryTimeFor(it.day), forecast.wind, forecast.gust) }\n"
    "        val uvSummaries = tempGraphSummaries.map { getUvIndexSummary(summaryTimeFor(it.day), forecast.uvIndex) }\n"
    "        return EssentialGraphsState.Success(",
    "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n"
    "        return EssentialGraphsState.Success(")
if s2 != s: ok("VM: computation reverted"); s = s2
else: warn("VM: computation not found")

s2 = s.replace(
    "        val backdrop: SkyBackdrop,\n        val windSummaries: List<WindSummary?>,\n        val uvSummaries: List<UvIndexSummary?>\n    ) : EssentialGraphsState",
    "        val backdrop: SkyBackdrop\n    ) : EssentialGraphsState")
if s2 != s: ok("VM: Success reverted"); s = s2
else: warn("VM: Success fields not found")

s2 = s.replace(
    "            backdrop = backdrop,\n            windSummaries = windSummaries,\n            uvSummaries = uvSummaries\n        )",
    "            backdrop = backdrop\n        )")
if s2 != s: ok("VM: Success call reverted"); s = s2
else: warn("VM: Success call not found")
open(p, "w").write(s)

# A2. Pager: the page no longer carries summaries
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsScreen.kt"
s = open(p).read()
s2 = s.replace(
    "                uvIndexMax = state.uvIndexGraphs.max,\n                windSummary = state.windSummaries[page],\n                uvSummary = state.uvSummaries[page],",
    "                uvIndexMax = state.uvIndexGraphs.max,")
if s2 != s: ok("Pager: summaries reverted"); open(p, "w").write(s2)
else: warn("Pager: anchor not found")

# A3. Page: signature + headers revert
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphPage.kt"
s = open(p).read()
s2 = s.replace(
    "    uvIndexMax: UvIndex,\n"
    "    windSummary: com.davidtakac.bura.summary.wind.WindSummary?,\n"
    "    uvSummary: com.davidtakac.bura.summary.uvindex.UvIndexSummary?,\n"
    "    precipGraph: PrecipitationGraph,",
    "    uvIndexMax: UvIndex,\n    precipGraph: PrecipitationGraph,")
if s2 != s: ok("Page: signature reverted"); s = s2
else: warn("Page: signature not found")

wind_inserted = (
    "        if (metric == null || metric == GraphMetric.Wind) {\n"
    "            if (metric == GraphMetric.Wind) {\n"
    "                windSummary?.let { ws ->\n"
    "                    item {\n"
    "                        com.davidtakac.bura.summary.wind.compose.WindSummary(\n"
    "                            state = ws,\n"
    "                            modifier = Modifier.fillMaxWidth()\n"
    "                        )\n"
    "                    }\n"
    "                }\n"
    "            }\n"
    "            item {")
s2 = s.replace(wind_inserted, "        if (metric == null || metric == GraphMetric.Wind) {\n            item {")
if s2 != s: ok("Page: wind header reverted"); s = s2
else: warn("Page: wind header not found")

uv_inserted = (
    "        if (metric == null || metric == GraphMetric.UvIndex) {\n"
    "            if (metric == GraphMetric.UvIndex) {\n"
    "                uvSummary?.let { us ->\n"
    "                    item {\n"
    "                        com.davidtakac.bura.summary.uvindex.compose.UvIndexSummary(\n"
    "                            state = us,\n"
    "                            modifier = Modifier.fillMaxWidth()\n"
    "                        )\n"
    "                    }\n"
    "                }\n"
    "            }\n"
    "            item {")
s2 = s.replace(uv_inserted, "        if (metric == null || metric == GraphMetric.UvIndex) {\n            item {")
if s2 != s: ok("Page: UV header reverted"); s = s2
else: warn("Page: UV header not found")
open(p, "w").write(s)

# ---------- B. Fix the gauge ----------
# B1. Hoist the @Composable string calls out of the Canvas
p = "app/src/main/java/com/davidtakac/bura/summary/pressure/compose/PressureGauge.kt"
s = open(p).read()
s2 = s.replace(
    "    val hpa = state.now.convertTo(Pressure.Unit.Hectopascal).value\n    val lowLabel = stringResource(R.string.pressure_gauge_low)",
    "    val hpa = state.now.convertTo(Pressure.Unit.Hectopascal).value\n"
    "    val valueText = state.now.valueString()\n"
    "    val unitText = state.now.unitString()\n"
    "    val lowLabel = stringResource(R.string.pressure_gauge_low)")
if s2 != s: ok("Gauge: strings hoisted"); s = s2
else: warn("Gauge: hoist anchor not found")
s2 = s.replace("measurer.measure(state.now.valueString(), valueStyle.copy(color = ink))",
               "measurer.measure(valueText, valueStyle.copy(color = ink))")
if s2 != s: ok("Gauge: value text fixed"); s = s2
else: warn("Gauge: value text not found")
s2 = s2.replace("measurer.measure(state.now.unitString(), unitStyle.copy(color = muted))",
                "measurer.measure(unitText, unitStyle.copy(color = muted))")
if s2 != s: ok("Gauge: unit text fixed"); s = s2
else: warn("Gauge: unit text not found")
open(p, "w").write(s)

# B2. The missing import
p = "app/src/main/java/com/davidtakac/bura/summary/pressure/compose/PressureSummary.kt"
s = open(p).read()
if "import androidx.compose.foundation.layout.fillMaxWidth" not in s:
    s = s.replace("import androidx.compose.foundation.layout.aspectRatio",
                  "import androidx.compose.foundation.layout.aspectRatio\nimport androidx.compose.foundation.layout.fillMaxWidth")
    ok("PressureSummary: fillMaxWidth imported")
else:
    warn("PressureSummary: import already present")
open(p, "w").write(s)

print()
print("\n".join(log))
