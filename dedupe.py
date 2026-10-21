log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# 1. Page: the doubled import block
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphPage.kt"
s = open(p).read()
block = ("\nimport androidx.compose.ui.text.font.FontStyle"
    "\nimport com.davidtakac.bura.common.compose.rememberDateTimeHourMinuteFormatter"
    "\nimport com.davidtakac.bura.forecast.parameters.temperature.valueString as tempValueString"
    "\nimport com.davidtakac.bura.forecast.parameters.uvindex.valueString as uvValueString"
    "\nimport com.davidtakac.bura.forecast.parameters.wind.valueString as windValueString")
if block + block in s:
    s = s.replace(block + block, block)
    ok("Page: duplicate imports collapsed")
else:
    warn("Page: duplicate import block not found as expected")

# 2. Page: the doubled BriefingText renderer
render_start = "@Composable\nprivate fun BriefingText(briefing: DayBriefing?, metric: GraphMetric?) {"
first = s.index(render_start)
second = s.index(render_start, first + 1)
end_of_second = s.index("\n@Composable\nfun EssentialGraphPageLoadingIndicator(", second)
s = s[:second] + s[end_of_second + 1:]
ok("Page: duplicate BriefingText removed")

# 3. Pager: the doubled argument
p2 = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsScreen.kt"
s2 = open(p2).read()
dbl = "                briefing = state.briefings[page],\n                briefing = state.briefings[page],"
if dbl in s2:
    s2 = s2.replace(dbl, "                briefing = state.briefings[page],")
    ok("Pager: duplicate briefing argument collapsed")
else:
    warn("Pager: duplicate argument not found")
open(p, "w").write(s)
open(p2, "w").write(s2)

print()
print("\n".join(log))
