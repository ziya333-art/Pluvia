log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

p = "app/src/main/java/com/davidtakac/bura/graphs/common/LineGraph.kt"
s = open(p).read()

# 1. Runtime imports
s2 = s.replace("import androidx.compose.runtime.Composable",
"""import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue""")
if s2 != s: ok("imports: runtime state"); s = s2
else: warn("imports anchor not found")

# 2. Scrub state + gesture on the Canvas
s2 = s.replace("""    plotUnderfillBrush: Brush? = null,
) {
    Canvas(modifier) {""",
"""    plotUnderfillBrush: Brush? = null,
) {
    var scrub by remember(plotPoints) { mutableStateOf<Float?>(null) }
    val curve = remember(plotPoints) { Curve(plotPoints.map { it.value }) }
    val scrubTimes = remember(plotPoints) { plotPoints.map { it.time } }
    Canvas(
        modifier.scrubGesture { x, w ->
            scrub = x?.let { px -> mapScrubPosition(px, w, scrubTimes, args) }
        }
    ) {""")
if s2 != s: ok("scrub state + gesture wired"); s = s2
else: warn("canvas anchor not found")

# 3. The call passes curve + scrub
s2 = s.replace("""            valueFormatter = valueFormatter,
            min = valueTicks.minOf { it.value },
            max = valueTicks.maxOf { it.value },
            now = now,
            args = args
        )""",
"""            valueFormatter = valueFormatter,
            curve = curve,
            scrub = scrub,
            min = valueTicks.minOf { it.value },
            max = valueTicks.maxOf { it.value },
            now = now,
            args = args
        )""")
if s2 != s: ok("call site carries scrub"); s = s2
else: warn("call site anchor not found")

# 4. Signature gains curve + scrub
s2 = s.replace("""private fun DrawScope.drawHorizontalAxisAndPlot(
    plotPoints: List<PlotPoint>,
    plotBrush: Brush,""",
"""private fun DrawScope.drawHorizontalAxisAndPlot(
    plotPoints: List<PlotPoint>,
    curve: Curve,
    scrub: Float?,
    plotBrush: Brush,""")
if s2 != s: ok("signature carries scrub"); s = s2
else: warn("signature anchor not found")

# 5. Straight segments become the curve
s2 = s.replace("""    val plotPath = Path()
    val plotFillPath = Path()
    fun movePlot(x: Float, y: Float) {
        with(plotPath) { if (isEmpty) moveTo(x, y) else lineTo(x, y) }
        with(plotFillPath) { if (isEmpty) moveTo(x, y) else lineTo(x, y) }
    }""",
"""    val plotPath = Path()
    val plotFillPath = Path()
    val plotXs = mutableListOf<Float>()
    val plotYs = mutableListOf<Float>()
    fun movePlot(x: Float, y: Float) {
        plotXs.add(x)
        plotYs.add(y)
    }""")
if s2 != s: ok("collectors replace straight segments"); s = s2
else: warn("movePlot anchor not found")

# 6. Trace the smooth curve before drawing
s2 = s.replace("""        drawGutterIcon(i, x, gutterIcons[i], args)
    }

    drawPlotLinePath(lastX, args) {""",
"""        drawGutterIcon(i, x, gutterIcons[i], args)
    }

    if (plotXs.size >= 2) {
        curve.trace(
            xs = plotXs,
            ys = plotYs,
            path = plotPath,
            area = plotFillPath,
            baseY = size.height - args.bottomGutter
        )
    }

    drawPlotLinePath(lastX, args) {""")
if s2 != s: ok("curve traced"); s = s2
else: warn("trace insertion anchor not found")

# 7. Round caps
s2 = s.replace("""                width = args.plotWidth,
                join = StrokeJoin.Round,
                cap = StrokeCap.Square""",
"""                width = args.plotWidth,
                join = StrokeJoin.Round,
                cap = StrokeCap.Round""")
if s2 != s: ok("caps rounded"); s = s2
else: warn("caps anchor not found")

# 8. The area closes itself now
s2 = s.replace("""    plotUnderfillBrush?.let {
        closePlotFillPath(plotFillPath, lastX, args)
        drawPath(
            plotFillPath,
            brush = it
        )
    }""",
"""    plotUnderfillBrush?.let {
        drawPath(
            plotFillPath,
            brush = it
        )
    }""")
if s2 != s: ok("area path self-closed"); s = s2
else: warn("underfill anchor not found")

# 9. The crosshair
s2 = s.replace("""    maxCenter?.let { (offset, value) ->
        drawLabeledPoint(
            label = valueFormatter(value),
            center = offset,
            args = args,
        )
    }

    return HorizontalAxisDrawLater(nowCenter)""",
"""    maxCenter?.let { (offset, value) ->
        drawLabeledPoint(
            label = valueFormatter(value),
            center = offset,
            args = args,
        )
    }

    scrub?.let { sPos ->
        if (plotXs.size >= 2) {
            val i0 = sPos.toInt().coerceIn(0, plotXs.size - 1)
            val i1 = (i0 + 1).coerceAtMost(plotXs.size - 1)
            val frac = (sPos - i0).coerceIn(0f, 1f)
            val cx = plotXs[i0] + (plotXs[i1] - plotXs[i0]) * frac
            val v = curve.at(sPos)
            val percent = (v - min) / range
            val plotHeight = size.height - args.topGutter - args.bottomGutter
            val cy = ((1 - percent) * plotHeight) + args.topGutter
            drawLine(
                color = args.axisColor,
                start = Offset(cx, args.topGutter),
                end = Offset(cx, size.height - args.bottomGutter),
                strokeWidth = args.axisWidth * 2
            )
            drawCircle(args.pointOutlineColor, args.pointCenterRadius * 2.5f, Offset(cx, cy))
            drawLabeledPoint(
                label = valueFormatter(v),
                center = Offset(cx, cy),
                args = args,
            )
        }
    }

    return HorizontalAxisDrawLater(nowCenter)""")
if s2 != s: ok("crosshair drawn"); s = s2
else: warn("crosshair anchor not found")

# 10. The x -> index helper
s2 = s + """
private fun mapScrubPosition(
    px: Float,
    width: Float,
    times: List<ZonedDateTime>,
    args: GraphArgs
): Float? {
    val plotW = width - args.endGutter - args.startGutter
    if (plotW <= 0f || times.size < 2) return null
    val pct = ((px - args.startGutter) / plotW).coerceIn(0f, 1f)
    val t0 = times.first().toInstant()
    val total = ChronoUnit.SECONDS.between(t0, times.last().toInstant())
    val tSec = (pct * total).toLong()
    for (i in 0 until times.size - 1) {
        val s0 = ChronoUnit.SECONDS.between(t0, times[i].toInstant())
        val s1 = ChronoUnit.SECONDS.between(t0, times[i + 1].toInstant())
        if (tSec <= s1) {
            return (if (s1 > s0) i + (tSec - s0).toFloat() / (s1 - s0) else i.toFloat())
                .coerceIn(0f, (times.size - 1).toFloat())
        }
    }
    return (times.size - 1).toFloat()
}
"""
if s2 != s: ok("scrub mapping helper appended"); s = s2

open(p, "w").write(s)
print()
print("\n".join(log))
