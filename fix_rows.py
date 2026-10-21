log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- 1. MatchedHeightRow.kt (new): the two-pass equal-height layout ----------
open("app/src/main/java/com/davidtakac/bura/summary/common/compose/MatchedHeightRow.kt", "w").write(
'''package com.davidtakac.bura.summary.common.compose

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.Layout
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.Dp

/**
 * A row whose children all match the height of the tallest, without intrinsic
 * measurements (which SubcomposeLayout children cannot answer).
 * Children are measured naturally once, then re-measured at the shared height.
 */
@Composable
fun MatchedHeightRow(
    spacing: Dp,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Layout(content = content, modifier = modifier) { measurables, constraints ->
        if (measurables.isEmpty()) return@Layout layout(0, 0) {}
        val spacingPx = spacing.roundToPx()
        val gapTotal = spacingPx * (measurables.size - 1)
        val childWidth = (constraints.maxWidth - gapTotal) / measurables.size
        val natural = measurables.map {
            it.measure(
                Constraints(
                    minWidth = childWidth,
                    maxWidth = childWidth,
                    minHeight = 0,
                    maxHeight = Constraints.Infinity
                )
            )
        }
        val height = natural.maxOf { it.height }
        val placed = measurables.map {
            it.measure(
                Constraints(
                    minWidth = childWidth,
                    maxWidth = childWidth,
                    minHeight = height,
                    maxHeight = height
                )
            )
        }
        layout(constraints.maxWidth, height) {
            var x = 0
            placed.forEach { p ->
                p.placeRelative(x, 0)
                x += p.width + spacingPx
            }
        }
    }
}
''')
ok("MatchedHeightRow.kt created")

# ---------- 2. SummaryScreen: the three Rows become MatchedHeightRows ----------
p = "app/src/main/java/com/davidtakac/bura/summary/SummaryScreen.kt"
s = open(p).read()

pairs = [
    ("PrecipitationSummary", "UvIndexSummary", "state.precip", "state.uvIndex", "onPrecipitationClick", "onUvIndexClick"),
    ("PressureSummary", "HumiditySummary", "state.pressure", "state.humidity", None, None),
    ("SunSummary", "MoonPhase", "state.sun", None, None, None),
]

count = 0
# The general shape: Row(fillMaxWidth + IntrinsicSize.Min, spacedBy 16) { A(weight 1f fillMaxHeight) B(weight 1f fillMaxHeight) }
import re
row_pattern = re.compile(
    r"            Row\(\n"
    r"                modifier = Modifier\n"
    r"                    \.fillMaxWidth\(\)\n"
    r"                    \.height\(IntrinsicSize\.Min\),\n"
    r"                horizontalArrangement = Arrangement\.spacedBy\(16\.dp\)\n"
    r"            \) \{",
)

def repl(m):
    global count
    count += 1
    return "            MatchedHeightRow(\n                spacing = 16.dp,\n                modifier = Modifier.fillMaxWidth()\n            ) {"

s2 = row_pattern.sub(repl, s)
if count == 3: ok("SummaryGrid: 3 rows converted")
else: warn("SummaryGrid: expected 3 rows, converted %d" % count); s = s
s = s2 if count > 0 else s

# 2b. The children lose weight(1f) — the layout assigns width now
s2 = s.replace(".weight(1f)\n                        .fillMaxHeight()", ".fillMaxHeight()")
n = s.count(".weight(1f)\n                        .fillMaxHeight()")
if s2 != s: ok("SummaryGrid: weight() removed from paired tiles")
else: warn("SummaryGrid: weight anchors not found (%d)" % n)
s = s2

# 2c. Import
if "import com.davidtakac.bura.summary.common.compose.MatchedHeightRow" not in s:
    s = s.replace("import androidx.compose.foundation.lazy.grid.GridCells",
                  "import androidx.compose.foundation.lazy.grid.GridCells\nimport com.davidtakac.bura.summary.common.compose.MatchedHeightRow")
    ok("SummaryScreen: MatchedHeightRow imported")
open(p, "w").write(s)

print()
print("\n".join(log))
