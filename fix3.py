log = []
def ok(m): log.append("OK   " + m)
def warn(m): log.append("WARN " + m)

# ---------- 1. ModernChart: init guard + two-param callback ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/common/ModernChart.kt"
s = open(p).read()
s2 = s.replace(
    "    init {\n"
    "        if (values.size < 2) return\n"
    "        val d = DoubleArray(values.size - 1) { values[it + 1] - values[it] }\n"
    "        m[0] = d[0]\n",
    "    init {\n"
    "        if (values.size >= 2) {\n"
    "        val d = DoubleArray(values.size - 1) { values[it + 1] - values[it] }\n"
    "        m[0] = d[0]\n")
if s2 != s: ok("Curve: init guard wrapped"); s = s2
else: warn("Curve: init anchor not found")
s2 = s.replace(
    "                m[k + 1] = t * b * dk\n"
    "            }\n"
    "        }\n"
    "    }\n"
    "\n"
    "    /** Value on the curve at fractional index [s]. */",
    "                m[k + 1] = t * b * dk\n"
    "            }\n"
    "        }\n"
    "        }\n"
    "    }\n"
    "\n"
    "    /** Value on the curve at fractional index [s]. */")
if s2 != s: ok("Curve: init brace closed"); s = s2
else: warn("Curve: closing brace anchor not found")

s2 = s.replace(
    " * scroll view. Reports the finger's x, then null on release.\n"
    " */\n"
    "fun Modifier.scrubGesture(onScrub: (Float?) -> Unit): Modifier = pointerInput(Unit) {",
    " * scroll view. Reports the finger's x and the element width, then null on release.\n"
    " */\n"
    "fun Modifier.scrubGesture(onScrub: (x: Float?, width: Float) -> Unit): Modifier = pointerInput(Unit) {")
if s2 != s: ok("scrubGesture: signature carries width"); s = s2
else: warn("scrubGesture: signature anchor not found")

s2 = s.replace("        onScrub(x)\n", "        onScrub(x, size.width.toFloat())\n")
if s2 != s: ok("scrubGesture: initial callback carries width"); s = s2
else: warn("scrubGesture: initial callback not found")
s2 = s2.replace("            onScrub(c.position.x)\n", "            onScrub(c.position.x, size.width.toFloat())\n")
if s2 != s: ok("scrubGesture: drag callback carries width"); s = s2
else: warn("scrubGesture: drag callback not found")
s2 = s2.replace("        onScrub(null)\n", "        onScrub(null, size.width.toFloat())\n")
if s2 != s: ok("scrubGesture: release callback carries width"); s = s2
else: warn("scrubGesture: release callback not found")
open(p, "w").write(s)

# ---------- 2. WindGraph: the callback gains w, the label hoists ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/wind/compose/WindGraph.kt"
s = open(p).read()
s2 = s.replace(
    "                .scrubGesture { x ->\n"
    "                    scrub = x?.let { px ->\n"
    "                        val usable = size.width.toFloat()\n"
    "                        val step = if (points.size > 1) usable / (points.size - 1) else usable\n"
    "                        (px / step).coerceIn(0f, points.lastIndex.toFloat())\n"
    "                    }\n"
    "                }",
    "                .scrubGesture { x, w ->\n"
    "                    scrub = x?.let { px ->\n"
    "                        val step = if (points.size > 1) w / (points.size - 1) else w\n"
    "                        (px / step).coerceIn(0f, points.lastIndex.toFloat())\n"
    "                    }\n"
    "                }")
if s2 != s: ok("WindGraph: scrub callback takes width"); s = s2
else: warn("WindGraph: scrub callback anchor not found")

s2 = s.replace(
    "    val maxIdx = points.indices.maxByOrNull { points[it].speed.value } ?: 0\n"
    "    var scrub by remember(state) { mutableStateOf<Float?>(null) }",
    "    val maxIdx = points.indices.maxByOrNull { points[it].speed.value } ?: 0\n"
    "    val maxLabelText = points[maxIdx].speed.string()\n"
    "    var scrub by remember(state) { mutableStateOf<Float?>(null) }")
if s2 != s: ok("WindGraph: max label hoisted to composable body"); s = s2
else: warn("WindGraph: hoist anchor not found")

s2 = s.replace(
    "            val maxLabel = measurer.measure(\n"
    "                points[maxIdx].speed.string(),\n"
    "                TextStyle(fontSize = 10.sp, color = onSurfaceVariant)\n"
    "            )",
    "            val maxLabel = measurer.measure(\n"
    "                maxLabelText,\n"
    "                TextStyle(fontSize = 10.sp, color = onSurfaceVariant)\n"
    "            )")
if s2 != s: ok("WindGraph: Canvas uses the hoisted label"); s = s2
else: warn("WindGraph: Canvas label anchor not found")
open(p, "w").write(s)

print()
print("\n".join(log))
