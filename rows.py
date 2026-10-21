log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- A. SummaryTile: the card stretches when its box does ----------
p = "app/src/main/java/com/davidtakac/bura/summary/common/compose/SummaryTile.kt"
s = open(p).read()
old_mod = """                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = if (minWidth < 300.dp) minWidth else 64.dp),"""
new_mod = """                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(min = if (minWidth < 300.dp) minWidth else 64.dp)
                    .fillMaxHeight(),"""
n = s.count(old_mod)
s2 = s.replace(old_mod, new_mod)
if n == 2: ok("SummaryTile: both Surfaces stretch (%d)" % n); s = s2
else: warn("SummaryTile: expected 2 surfaces, found %d" % n)
if "import androidx.compose.foundation.layout.fillMaxHeight" not in s:
    s = s.replace("import androidx.compose.foundation.layout.fillMaxSize",
                  "import androidx.compose.foundation.layout.fillMaxHeight\nimport androidx.compose.foundation.layout.fillMaxSize")
    ok("SummaryTile: fillMaxHeight imported")
open(p, "w").write(s)

# ---------- B. SummaryGrid: pairs become matched rows ----------
p = "app/src/main/java/com/davidtakac/bura/summary/SummaryScreen.kt"
s = open(p).read()
try:
    start = s.index("        item {\n            PrecipitationSummary(")
    end = s.index("        item(span = { GridItemSpan(maxLineSpan) }) {\n            VisibilitySummary(")
    rows = '''        item(span = { GridItemSpan(maxLineSpan) }) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                PrecipitationSummary(
                    state = state.precip,
                    onClick = onPrecipitationClick,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                )
                UvIndexSummary(
                    state = state.uvIndex,
                    onClick = onUvIndexClick,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                )
            }
        }
        item(span = { GridItemSpan(maxLineSpan) }) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                PressureSummary(
                    state = state.pressure,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                )
                HumiditySummary(
                    state = state.humidity,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                )
            }
        }
        item(span = { GridItemSpan(maxLineSpan) }) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                SunSummary(
                    state = state.sun,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                )
                com.davidtakac.bura.summary.moon.compose.MoonPhase(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight()
                )
            }
        }
'''
    s = s[:start] + rows + s[end:]
    ok("SummaryGrid: three matched rows")
except ValueError:
    warn("SummaryGrid: anchors not found")

anchor = "import androidx.compose.foundation.lazy.grid.GridCells"
for imp in [
    "import androidx.compose.foundation.layout.IntrinsicSize",
    "import androidx.compose.foundation.layout.Row",
    "import androidx.compose.foundation.layout.fillMaxHeight",
    "import androidx.compose.foundation.layout.height",
]:
    if imp not in s:
        s = s.replace(anchor, anchor + "\n" + imp)
        ok("SummaryScreen: %s" % imp.split(".")[-1] + " imported")
open(p, "w").write(s)

print()
print("\\n".join(log))
