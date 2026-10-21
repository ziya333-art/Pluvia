log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- 1. DayBriefing.kt (new): the per-day briefing data ----------
open("app/src/main/java/com/davidtakac/bura/graphs/DayBriefing.kt", "w").write(
'''package com.davidtakac.bura.graphs

import com.davidtakac.bura.forecast.parameters.gust.GustPeriod
import com.davidtakac.bura.forecast.parameters.pop.PopPeriod
import com.davidtakac.bura.forecast.parameters.temperature.Temperature
import com.davidtakac.bura.forecast.parameters.temperature.TemperaturePeriod
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndex
import com.davidtakac.bura.forecast.parameters.uvindex.UvIndexPeriod
import com.davidtakac.bura.forecast.parameters.wind.WindSpeed
import java.time.LocalDate
import java.time.ZonedDateTime

data class DayBriefing(
    val tempMin: Temperature?,
    val tempMax: Temperature?,
    val tempMaxAt: ZonedDateTime?,
    val gustMax: WindSpeed?,
    val gustMaxAt: ZonedDateTime?,
    val uvMax: UvIndex?,
    val uvMaxAt: ZonedDateTime?,
    val popMax: Int?,
    val popMaxAt: ZonedDateTime?
)

fun getDayBriefing(
    day: LocalDate,
    temperaturePeriod: TemperaturePeriod,
    gustPeriod: GustPeriod,
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
    val uvMoment = uvs?.maxByOrNull { it.uvIndex.value }
    val popMoment = pops?.maxByOrNull { it.pop.value }
    return DayBriefing(
        tempMin = tempMinMoment?.temperature,
        tempMax = tempMaxMoment?.temperature,
        tempMaxAt = tempMaxMoment?.timeZdt,
        gustMax = gustMoment?.speed,
        gustMaxAt = gustMoment?.timeZdt,
        uvMax = uvMoment?.uvIndex,
        uvMaxAt = uvMoment?.timeZdt,
        popMax = popMoment?.pop?.value,
        popMaxAt = popMoment?.timeZdt
    )
}
''')
ok("DayBriefing.kt created")

# ---------- 2. ViewModel: one briefing per day ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsViewModel.kt"
s = open(p).read()
s2 = s.replace(
    "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n        return EssentialGraphsState.Success(",
    "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n"
    "        val briefings = tempGraphSummaries.map { getDayBriefing(it.day, forecast.temperature, forecast.gust, forecast.uvIndex, forecast.pop) }\n"
    "        return EssentialGraphsState.Success(")
if s2 != s: ok("VM: briefings computed"); s = s2
else: warn("VM: computation anchor not found")
s2 = s.replace(
    "        val backdrop: SkyBackdrop\n    ) : EssentialGraphsState",
    "        val backdrop: SkyBackdrop,\n        val briefings: List<DayBriefing>\n    ) : EssentialGraphsState")
if s2 != s: ok("VM: Success gains briefings"); s = s2
else: warn("VM: Success anchor not found")
s2 = s.replace(
    "            backdrop = backdrop\n        )",
    "            backdrop = backdrop,\n            briefings = briefings\n        )")
if s2 != s: ok("VM: Success call carries briefings"); s = s2
else: warn("VM: Success call anchor not found")
open(p, "w").write(s)

# ---------- 3. Pager: the page receives its day's briefing ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsScreen.kt"
s = open(p).read()
s2 = s.replace(
    "                uvIndexMax = state.uvIndexGraphs.max,",
    "                uvIndexMax = state.uvIndexGraphs.max,\n                briefing = state.briefings[page],")
if s2 != s: ok("Pager: briefing threaded"); open(p, "w").write(s2)
else: warn("Pager: anchor not found")

# ---------- 4. Page: signature, the sentence item, the renderer ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphPage.kt"
s = open(p).read()

anchor = "import com.davidtakac.bura.graphs.common.GraphArgs"
s2 = s.replace(anchor, anchor +
    "\nimport androidx.compose.ui.text.font.FontStyle"
    "\nimport com.davidtakac.bura.common.compose.rememberDateTimeHourMinuteFormatter"
    "\nimport com.davidtakac.bura.forecast.parameters.temperature.valueString as tempValueString"
    "\nimport com.davidtakac.bura.forecast.parameters.uvindex.valueString as uvValueString"
    "\nimport com.davidtakac.bura.forecast.parameters.wind.valueString as windValueString")
if s2 != s: ok("Page: imports added"); s = s2
else: warn("Page: import anchor not found")

s2 = s.replace(
    "    now: Instant,\n    metric: GraphMetric?,\n    summary: TemperatureGraphSummary,",
    "    now: Instant,\n    metric: GraphMetric?,\n    briefing: DayBriefing?,\n    summary: TemperatureGraphSummary,")
if s2 != s: ok("Page: signature gains briefing"); s = s2
else: warn("Page: signature anchor not found")

s2 = s.replace(
    "        modifier = Modifier.fillMaxSize()\n    ) {\n        if (metric == null || metric == GraphMetric.Temperature) {",
    "        modifier = Modifier.fillMaxSize()\n    ) {\n        if (metric != null) {\n            item {\n                BriefingText(briefing = briefing, metric = metric)\n            }\n        }\n        if (metric == null || metric == GraphMetric.Temperature) {")
if s2 != s: ok("Page: briefing item placed"); s = s2
else: warn("Page: item anchor not found")

renderer = '''@Composable
private fun BriefingText(briefing: DayBriefing?, metric: GraphMetric?) {
    if (briefing == null) return
    val formatter = rememberDateTimeHourMinuteFormatter()
    val text: String? = when (metric) {
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
            val gust = briefing.gustMax ?: return
            stringResource(
                R.string.briefing_wind,
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
        else -> null
    } ?: return
    Text(
        text = text,
        style = MaterialTheme.typography.bodyMedium,
        fontStyle = FontStyle.Italic,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
        modifier = Modifier.fillMaxWidth()
    )
}

'''
s2 = s.replace("@Composable\nfun EssentialGraphPageLoadingIndicator(",
               renderer + "@Composable\nfun EssentialGraphPageLoadingIndicator(")
if s2 != s: ok("Page: BriefingText renderer added"); s = s2
else: warn("Page: renderer anchor not found")
open(p, "w").write(s)

# ---------- 5. The sentences (English base; Weblate follows) ----------
p = "app/src/main/res/values/strings.xml"
s = open(p).read()
if "briefing_temperature" not in s:
    s = s.replace("</resources>",
        '    <string name="briefing_temperature">Temperatures range from %1$s to %2$s. The warmest part of the day is around %3$s.</string>\n'
        '    <string name="briefing_wind">Gusts up to %1$s around %2$s.</string>\n'
        '    <string name="briefing_uv">Peaking at %1$s around %2$s.</string>\n'
        '    <string name="briefing_pop">Chance of precipitation peaks at %1$s around %2$s.</string>\n'
        "</resources>")
    ok("strings.xml: four briefings added")
else:
    warn("strings.xml: briefings already present")
open(p, "w").write(s)

print()
print("\n".join(log))
