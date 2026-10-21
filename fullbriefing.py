log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- 1. DayBriefing: gains wind speed + time ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/DayBriefing.kt"
s = open(p).read()
s2 = s.replace(
    "import com.davidtakac.bura.forecast.parameters.wind.WindSpeed",
    "import com.davidtakac.bura.forecast.parameters.wind.WindPeriod\nimport com.davidtakac.bura.forecast.parameters.wind.WindSpeed")
if s2 != s: ok("DayBriefing: WindPeriod import"); s = s2
else: warn("DayBriefing: import anchor not found")

s2 = s.replace(
    "    val gustMax: WindSpeed?,\n    val gustMaxAt: ZonedDateTime?,",
    "    val gustMax: WindSpeed?,\n    val gustMaxAt: ZonedDateTime?,\n    val windMax: WindSpeed?,\n    val windMaxAt: ZonedDateTime?,")
if s2 != s: ok("DayBriefing: fields added"); s = s2
else: warn("DayBriefing: fields anchor not found")

s2 = s.replace(
    "    gustPeriod: GustPeriod,",
    "    gustPeriod: GustPeriod,\n    windPeriod: WindPeriod,")
if s2 != s: ok("DayBriefing: signature gains windPeriod"); s = s2
else: warn("DayBriefing: signature anchor not found")

s2 = s.replace(
    "    val gustMoment = gusts?.maxByOrNull { it.speed.value }",
    "    val gustMoment = gusts?.maxByOrNull { it.speed.value }\n"
    "    val winds = windPeriod.dayMomentsOn(day)\n"
    "    val windMoment = winds?.maxByOrNull { it.wind.speed.value }")
if s2 != s: ok("DayBriefing: wind max computed"); s = s2
else: warn("DayBriefing: computation anchor not found")

s2 = s.replace(
    "        gustMax = gustMoment?.speed,\n        gustMaxAt = gustMoment?.timeZdt,",
    "        gustMax = gustMoment?.speed,\n        gustMaxAt = gustMoment?.timeZdt,\n"
    "        windMax = windMoment?.wind?.speed,\n        windMaxAt = windMoment?.timeZdt,")
if s2 != s: ok("DayBriefing: wind fields carried"); s = s2
else: warn("DayBriefing: carry anchor not found")
open(p, "w").write(s)

# ---------- 2. VM: passes the wind period ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsViewModel.kt"
s = open(p).read()
s2 = s.replace(
    "val briefings = tempGraphSummaries.map { getDayBriefing(it.day, forecast.temperature, forecast.gust, forecast.uvIndex, forecast.pop) }",
    "val briefings = tempGraphSummaries.map { getDayBriefing(it.day, forecast.temperature, forecast.gust, windPeriod = forecast.wind, uvIndexPeriod = forecast.uvIndex, popPeriod = forecast.pop) }")
if s2 != s: ok("VM: wind period passed"); open(p, "w").write(s2)
else: warn("VM: anchor not found")

# ---------- 3. Page: move below the chart, restyle as Stratus's section ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphPage.kt"
s = open(p).read()

item_block = (
    "        if (metric != null) {\n"
    "            item {\n"
    "                BriefingText(briefing = briefing, metric = metric)\n"
    "            }\n"
    "        }\n")
if item_block in s:
    s = s.replace(item_block, "", 1)
    ok("Page: top item removed")
else:
    warn("Page: top item not found")

credit_anchor = (
    "        item {\n"
    "            Text(\n"
    "                text = stringResource(id = R.string.credit_weather),")
if credit_anchor in s:
    s = s.replace(credit_anchor, item_block + credit_anchor, 1)
    ok("Page: section placed below the charts")
else:
    warn("Page: credit anchor not found")

# Restyle the renderer: the panel section
s2 = s.replace(
    "        else -> null\n"
    "    } ?: return\n"
    "    Text(\n"
    "        text = text,\n"
    "        style = MaterialTheme.typography.bodyMedium,\n"
    "        fontStyle = FontStyle.Italic,\n"
    "        color = MaterialTheme.colorScheme.onSurfaceVariant,\n"
    "        modifier = Modifier.fillMaxWidth()\n"
    "    )\n"
    "}",
    "        else -> return\n"
    "    }\n"
    "    Column(modifier = Modifier.fillMaxWidth()) {\n"
    "        Text(\n"
    "            text = stringResource(R.string.briefing_daily_summary),\n"
    "            style = MaterialTheme.typography.titleSmall,\n"
    "            color = MaterialTheme.colorScheme.onSurfaceVariant\n"
    "        )\n"
    "        Text(\n"
    "            text = text,\n"
    "            style = MaterialTheme.typography.bodyMedium,\n"
    "            color = MaterialTheme.colorScheme.onSurface,\n"
    "            modifier = Modifier\n"
    "                .fillMaxWidth()\n"
    "                .clip(MaterialTheme.shapes.medium)\n"
    "                .background(MaterialTheme.colorScheme.surfaceContainer)\n"
    "                .padding(14.dp)\n"
    "        )\n"
    "    }\n"
    "}")
if s2 != s: ok("Page: renderer restyled as the panel section"); s = s2
else: warn("Page: renderer anchor not found")

# The wind sentence uses both speeds now
s2 = s.replace(
    "        GraphMetric.Wind -> {\n"
    "            val gust = briefing.gustMax ?: return\n"
    "            stringResource(\n"
    "                R.string.briefing_wind,\n"
    "                gust.windValueString(),\n"
    "                briefing.gustMaxAt?.let { formatter.format(it.toLocalTime()) } ?: \"\"\n"
    "            )\n"
    "        }",
    "        GraphMetric.Wind -> {\n"
    "            val wind = briefing.windMax ?: return\n"
    "            val gust = briefing.gustMax ?: return\n"
    "            stringResource(\n"
    "                R.string.briefing_wind,\n"
    "                wind.windValueString(),\n"
    "                gust.windValueString(),\n"
    "                briefing.gustMaxAt?.let { formatter.format(it.toLocalTime()) } ?: \"\"\n"
    "            )\n"
    "        }")
if s2 != s: ok("Page: wind sentence carries speed + gust"); s = s2
else: warn("Page: wind sentence anchor not found")

# Imports the panel needs
for imp, anchor in [
    ("import androidx.compose.foundation.background", "import androidx.compose.foundation.Canvas"),
    ("import androidx.compose.ui.draw.clip", "import androidx.compose.foundation.background"),
    ("import androidx.compose.foundation.layout.padding", "import androidx.compose.ui.draw.clip"),
    ("import androidx.compose.ui.unit.dp", "import androidx.compose.foundation.layout.padding"),
]:
    if imp not in s:
        s = s.replace(anchor, imp + "\n" + anchor)
        ok("Page: %s" % imp.split(".")[-1] + " imported")
open(p, "w").write(s)

# ---------- 4. Strings: the title + the richer wind sentence ----------
p = "app/src/main/res/values/strings.xml"
s = open(p).read()
s2 = s.replace(
    '<string name="briefing_wind">Gusts up to %1$s around %2$s.</string>',
    '<string name="briefing_wind">Winds up to %1$s with gusts to %2$s, peaking around %3$s.</string>')
if s2 != s: ok("strings: wind sentence enriched"); s = s2
else: warn("strings: wind anchor not found")
if "briefing_daily_summary" not in s:
    s = s.replace("</resources>",
        '    <string name="briefing_daily_summary">Daily Summary</string>\n'
        "</resources>")
    ok("strings: Daily Summary title added")
open(p, "w").write(s)

print()
print("\n".join(log))
