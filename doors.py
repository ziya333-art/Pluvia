import re
log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- A. VM fix: define the backdrop ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsViewModel.kt"
s = open(p).read()
s2 = s.replace(
    "        val uvIndexGraphs = getUvIndexGraphs(now = now, uvIndexPeriod = forecast.uvIndex) ?: return EssentialGraphsState.Outdated\n        return EssentialGraphsState.Success(",
    "        val uvIndexGraphs = getUvIndexGraphs(now = now, uvIndexPeriod = forecast.uvIndex) ?: return EssentialGraphsState.Outdated\n"
    "        val condNow = forecast.condition.day ?: forecast.condition.night ?: return EssentialGraphsState.Outdated\n"
    "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n"
    "        return EssentialGraphsState.Success(")
if s2 != s: ok("VM: backdrop defined (day/night representative)"); open(p, "w").write(s2)
else: warn("VM: anchor not found")

# ---------- B. WindSummary.kt ----------
p = "app/src/main/java/com/davidtakac/bura/summary/wind/compose/WindSummary.kt"
s = open(p).read()
s2 = s.replace("fun WindSummary(state: WindSummary, modifier: Modifier = Modifier) {",
               "fun WindSummary(state: WindSummary, modifier: Modifier = Modifier, onClick: (() -> Unit)? = null) {")
if s2 != s: ok("WindSummary: signature"); s = s2
else: warn("WindSummary: signature anchor not found")
s2 = s.replace("""    SummaryTile(
        label = { Text(text = stringResource(R.string.wind_label)) },""",
"""    SummaryTile(
        onClick = onClick,
        label = { Text(text = stringResource(R.string.wind_label)) },""")
if s2 != s: ok("WindSummary: tile door"); open(p, "w").write(s2)
else: warn("WindSummary: tile anchor not found")

# ---------- C. UvIndexSummary.kt ----------
p = "app/src/main/java/com/davidtakac/bura/summary/uvindex/compose/UvIndexSummary.kt"
s = open(p).read()
s2 = s.replace("fun UvIndexSummary(state: UvIndexSummary, modifier: Modifier = Modifier) {",
               "fun UvIndexSummary(state: UvIndexSummary, modifier: Modifier = Modifier, onClick: (() -> Unit)? = null) {")
if s2 != s: ok("UvIndexSummary: signature"); s = s2
else: warn("UvIndexSummary: signature anchor not found")
s2 = s.replace("""    SummaryTile(
        label = { Text(text = stringResource(R.string.uv_index)) },""",
"""    SummaryTile(
        onClick = onClick,
        label = { Text(text = stringResource(R.string.uv_index)) },""")
if s2 != s: ok("UvIndexSummary: tile door"); open(p, "w").write(s2)
else: warn("UvIndexSummary: tile anchor not found")

# ---------- D. SummaryDestination.kt ----------
p = "app/src/main/java/com/davidtakac/bura/summary/SummaryDestination.kt"
s = open(p).read()
s2 = s.replace("    onPrecipitationClick: () -> Unit,",
               "    onPrecipitationClick: () -> Unit,\n    onWindClick: () -> Unit,\n    onUvIndexClick: () -> Unit,")
if s2 != s: ok("SummaryDestination: signature"); s = s2
else: warn("SummaryDestination: signature anchor not found")
s2 = s.replace("        onPrecipitationClick = onPrecipitationClick,",
               "        onPrecipitationClick = onPrecipitationClick,\n        onWindClick = onWindClick,\n        onUvIndexClick = onUvIndexClick,")
if s2 != s: ok("SummaryDestination: pass-through"); open(p, "w").write(s2)
else: warn("SummaryDestination: pass anchor not found")

# ---------- E. SummaryScreen.kt ----------
p = "app/src/main/java/com/davidtakac/bura/summary/SummaryScreen.kt"
s = open(p).read()
n = s.count("    onPrecipitationClick: () -> Unit,")
s2 = s.replace("    onPrecipitationClick: () -> Unit,",
               "    onPrecipitationClick: () -> Unit,\n    onWindClick: () -> Unit,\n    onUvIndexClick: () -> Unit,")
if s2 != s: ok("SummaryScreen: signatures (%d occurrences)" % n); s = s2
else: warn("SummaryScreen: signature anchor not found")
s2 = s.replace("""            WindSummary(
                state = state.wind,
                modifier = Modifier.fillMaxWidth()
            )""",
"""            WindSummary(
                state = state.wind,
                onClick = onWindClick,
                modifier = Modifier.fillMaxWidth()
            )""")
if s2 != s: ok("SummaryScreen: wind tile wired"); s = s2
else: warn("SummaryScreen: wind tile anchor not found")
s2 = s.replace("""            UvIndexSummary(
                state = state.uvIndex,
                modifier = Modifier.fillMaxWidth()
            )""",
"""            UvIndexSummary(
                state = state.uvIndex,
                onClick = onUvIndexClick,
                modifier = Modifier.fillMaxWidth()
            )""")
if s2 != s: ok("SummaryScreen: uv tile wired"); s = s2
else: warn("SummaryScreen: uv tile anchor not found")
m = re.search(r"onHourlyClick = onHourlySectionClick,", s)
if m:
    s = s[:m.start()] + "onHourlyClick = onHourlySectionClick,\n                        onWindClick = onWindClick,\n                        onUvIndexClick = onUvIndexClick," + s[m.end():]
    ok("SummaryScreen: call site threaded")
else:
    m = re.search(r"SummaryGrid\(\s*\n\s*state = it,", s)
    if m:
        s = s[:m.end()] + "\n                        onWindClick = onWindClick,\n                        onUvIndexClick = onUvIndexClick," + s[m.end():]
        ok("SummaryScreen: call site threaded (fallback)")
    else:
        warn("SummaryScreen: call site anchor not found")
open(p, "w").write(s)

# ---------- F. AppNavHost.kt ----------
p = "app/src/main/java/com/davidtakac/bura/AppNavHost.kt"
s = open(p).read()
m = re.search(r"\n(\s*)onHourlySectionClick = \{", s)
if m:
    insert = ("\n" + m.group(1) + 'onWindClick = { controller.navigate("essential-graphs?metric=wind") },'
              "\n" + m.group(1) + 'onUvIndexClick = { controller.navigate("essential-graphs?metric=uv") },')
    s = s[:m.start()] + insert + s[m.start():]
    ok("AppNavHost: wind + uv routes")
else:
    warn("AppNavHost: onHourlySectionClick anchor not found")
open(p, "w").write(s)

print()
print("\n".join(log))
