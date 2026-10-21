log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- A. The ViewModel ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsViewModel.kt"
s = open(p).read()

anchor = "import com.davidtakac.bura.theme.weatherBackdrop"
s2 = s.replace(anchor, anchor +
    "\nimport com.davidtakac.bura.summary.wind.getWindSummary"
    "\nimport com.davidtakac.bura.summary.wind.WindSummary"
    "\nimport com.davidtakac.bura.summary.uvindex.getUvIndexSummary"
    "\nimport com.davidtakac.bura.summary.uvindex.UvIndexSummary"
    "\nimport java.time.LocalDate"
    "\nimport java.time.ZonedDateTime")
if s2 != s: ok("VM: imports"); s = s2
else: warn("VM: import anchor not found")

anchor = "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n        return EssentialGraphsState.Success("
s2 = s.replace(anchor,
    "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n"
    "        fun summaryTimeFor(day: LocalDate): ZonedDateTime =\n"
    "            if (day == now.toLocalDate()) now else day.atTime(12, 0).atZone(now.zone)\n"
    "        val windSummaries = tempGraphSummaries.map { getWindSummary(summaryTimeFor(it.day), forecast.wind, forecast.gust) }\n"
    "        val uvSummaries = tempGraphSummaries.map { getUvIndexSummary(summaryTimeFor(it.day), forecast.uvIndex) }\n"
    "        return EssentialGraphsState.Success(")
if s2 != s: ok("VM: per-day summaries computed"); s = s2
else: warn("VM: computation anchor not found")

s2 = s.replace("        val backdrop: SkyBackdrop\n    ) : EssentialGraphsState",
              "        val backdrop: SkyBackdrop,\n        val windSummaries: List<WindSummary?>,\n        val uvSummaries: List<UvIndexSummary?>\n    ) : EssentialGraphsState")
if s2 != s: ok("VM: Success gains the lists"); s = s2
else: warn("VM: Success anchor not found")

s2 = s.replace("            backdrop = backdrop\n        )",
              "            backdrop = backdrop,\n            windSummaries = windSummaries,\n            uvSummaries = uvSummaries\n        )")
if s2 != s: ok("VM: Success call carries the lists"); s = s2
else: warn("VM: Success call anchor not found")
open(p, "w").write(s)

# ---------- B. The Pager (EssentialGraphsScreen.kt) ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsScreen.kt"
s = open(p).read()
s2 = s.replace("                uvIndexMax = state.uvIndexGraphs.max,",
               "                uvIndexMax = state.uvIndexGraphs.max,\n                windSummary = state.windSummaries[page],\n                uvSummary = state.uvSummaries[page],")
if s2 != s: ok("Pager: page receives its summaries"); open(p, "w").write(s2)
else: warn("Pager: anchor not found")

# ---------- C. The Page (EssentialGraphPage.kt) ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphPage.kt"
s = open(p).read()

s2 = s.replace("    uvIndexMax: UvIndex,\n    precipGraph: PrecipitationGraph,",
    "    uvIndexMax: UvIndex,\n"
    "    windSummary: com.davidtakac.bura.summary.wind.WindSummary?,\n"
    "    uvSummary: com.davidtakac.bura.summary.uvindex.UvIndexSummary?,\n"
    "    precipGraph: PrecipitationGraph,")
if s2 != s: ok("Page: signature gains the summaries"); s = s2
else: warn("Page: signature anchor not found")

wind_anchor = "        if (metric == null || metric == GraphMetric.Wind) {\n            item {"
wind_header = (
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
s2 = s.replace(wind_anchor, wind_header)
if s2 != s: ok("Page: wind room gains its header"); s = s2
else: warn("Page: wind anchor not found")

uv_anchor = "        if (metric == null || metric == GraphMetric.UvIndex) {\n            item {"
uv_header = (
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
s2 = s.replace(uv_anchor, uv_header)
if s2 != s: ok("Page: UV room gains its header"); s = s2
else: warn("Page: UV anchor not found")
open(p, "w").write(s)

print()
print("\n".join(log))
