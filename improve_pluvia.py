import re

log = []
def ok(msg): log.append("OK   " + msg)
def warn(msg): log.append("WARN " + msg)

def retarget(s, callback, old, new):
    i = s.index(callback)
    j = s.index(old, i)
    return s[:j] + new + s[j + len(old):]

# ---------- 1. GraphMetric.kt ----------
open("app/src/main/java/com/davidtakac/bura/graphs/GraphMetric.kt", "w").write(
"""package com.davidtakac.bura.graphs

enum class GraphMetric {
    Temperature, Wind, UvIndex, Precipitation, Pop;

    companion object {
        fun fromRoute(value: String?): GraphMetric? = when (value?.lowercase()) {
            "temperature" -> Temperature
            "wind" -> Wind
            "uv" -> UvIndex
            "precipitation" -> Precipitation
            "pop" -> Pop
            else -> null
        }
    }
}
""")
ok("GraphMetric.kt created")

# ---------- 2. AppNavHost.kt ----------
p = "app/src/main/java/com/davidtakac/bura/AppNavHost.kt"
s = open(p).read()
s2 = re.sub(r"(package com\.davidtakac\.bura\n)",
            "\\1\nimport com.davidtakac.bura.graphs.GraphMetric\n", s, count=1)
if s2 != s: ok("AppNavHost: import added"); s = s2
else: warn("AppNavHost: package anchor not found")

s2 = s.replace('route = "essential-graphs?initialDay={initialDay}"',
               'route = "essential-graphs?initialDay={initialDay}&metric={metric}"')
if s2 != s: ok("AppNavHost: route extended"); s = s2
else: warn("AppNavHost: route literal not found")

s2 = s.replace("""                navArgument("initialDay") {
                    nullable = true
                    defaultValue = null
                    type = NavType.StringType
                }""",
"""                navArgument("initialDay") {
                    nullable = true
                    defaultValue = null
                    type = NavType.StringType
                },
                navArgument("metric") {
                    nullable = true
                    defaultValue = null
                    type = NavType.StringType
                }""")
if s2 != s: ok("AppNavHost: metric argument added"); s = s2
else: warn("AppNavHost: navArgument block not found")

s2 = s.replace('initialDay = backStackEntry.arguments?.getString("initialDay")?.let(LocalDate::parse),',
'''initialDay = backStackEntry.arguments?.getString("initialDay")?.let(LocalDate::parse),
                metric = GraphMetric.fromRoute(backStackEntry.arguments?.getString("metric")),''')
if s2 != s: ok("AppNavHost: destination receives metric"); s = s2
else: warn("AppNavHost: destination call not found")

try:
    s = retarget(s, "onHourlySectionClick",
                 'navigate("essential-graphs")',
                 'navigate("essential-graphs?metric=temperature")')
    ok("AppNavHost: hourly -> temperature")
    s = retarget(s, "onDayClick",
                 'navigate("essential-graphs?initialDay=$it")',
                 'navigate("essential-graphs?initialDay=$it&metric=temperature")')
    ok("AppNavHost: day -> temperature")
    s = retarget(s, "onPrecipitationClick",
                 'navigate("essential-graphs")',
                 'navigate("essential-graphs?metric=precipitation")')
    ok("AppNavHost: precip -> precipitation")
except ValueError as e:
    warn("AppNavHost: retarget failed: " + str(e))
open(p, "w").write(s)

# ---------- 3. EssentialGraphsDestination.kt ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsDestination.kt"
s = open(p).read()
s2 = s.replace("fun EssentialGraphsDestination(\n    initialDay: LocalDate?,",
              "fun EssentialGraphsDestination(\n    initialDay: LocalDate?,\n    metric: GraphMetric?,")
s2 = s2.replace("EssentialGraphsScreen(\n        initialDay = initialDay,",
               "EssentialGraphsScreen(\n        initialDay = initialDay,\n        metric = metric,")
if "metric = metric," in s2: ok("Destination: metric threaded"); open(p, "w").write(s2)
else: warn("Destination: anchors not found")

# ---------- 4. EssentialGraphsScreen.kt ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsScreen.kt"
s = open(p).read()
s2 = s.replace("import androidx.compose.material3.ExperimentalMaterial3Api",
"""import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Box
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale""")
if s2 != s: ok("Screen: imports added"); s = s2
else: warn("Screen: import anchor not found")

NEW_MAIN = '''@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EssentialGraphsScreen(
    initialDay: LocalDate?,
    metric: GraphMetric?,
    state: EssentialGraphsState,
    onTryAgainClick: () -> Unit,
    onSelectPlaceClick: () -> Unit,
    onBackClick: () -> Unit
) {
    val sky = (state as? EssentialGraphsState.Success)?.backdrop
    Box(modifier = Modifier.fillMaxSize()) {
        if (sky != null) {
            Image(
                painter = painterResource(sky.imageRes),
                contentDescription = null,
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop
            )
        }
        MaterialTheme(
            colorScheme = darkColorScheme(
                surface = Color.Black.copy(alpha = 0.38f),
                surfaceVariant = Color.Black.copy(alpha = 0.38f),
                surfaceContainer = Color.Black.copy(alpha = 0.38f),
                surfaceContainerHigh = Color.Black.copy(alpha = 0.38f),
                background = Color.Transparent
            )
        ) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Text(
                                stringResource(
                                    when (metric) {
                                        GraphMetric.Wind -> R.string.cond_screen_wind
                                        GraphMetric.UvIndex -> R.string.cond_screen_uv_index
                                        GraphMetric.Pop -> R.string.cond_screen_pop
                                        GraphMetric.Precipitation -> R.string.cond_screen_precip
                                        else -> R.string.cond_screen_title
                                    }
                                )
                            )
                        },
                        navigationIcon = {
                            IconButton(onClick = onBackClick) {
                                Icon(
                                    painter = painterResource(id = R.drawable.arrow_back),
                                    contentDescription = null
                                )
                            }
                        }
                    )
                }
            ) { contentPadding ->
                Crossfade(
                    targetState = state,
                    modifier = Modifier
                        .padding(
                            start = contentPadding.calculateStartPadding(LocalLayoutDirection.current),
                            end = contentPadding.calculateEndPadding(LocalLayoutDirection.current),
                            top = contentPadding.calculateTopPadding(),
                        ),
                    label = "State crossfade"
                ) {
                    val bottomContentPadding = contentPadding.calculateBottomPadding()
                    val pageContentPadding = PaddingValues(
                        start = 16.dp,
                        end = 16.dp,
                        top = 16.dp,
                        bottom = bottomContentPadding + 16.dp,
                    )
                    when (it) {
                        is EssentialGraphsState.Success -> Pager(
                            state = it,
                            initialDay = initialDay,
                            metric = metric,
                            pageContentPadding = pageContentPadding,
                            modifier = Modifier.fillMaxSize()
                        )

                        EssentialGraphsState.Loading, EssentialGraphsState.Initial -> EssentialGraphsLoadingIndicator(
                            pageContentPadding = pageContentPadding,
                            modifier = Modifier.padding(bottom = bottomContentPadding).fillMaxSize()
                        )

                        EssentialGraphsState.FailedToDownload -> FailedToDownloadErrorScreen(
                            modifier = Modifier.padding(bottom = bottomContentPadding).fillMaxSize(),
                            onTryAgainClick = onTryAgainClick
                        )

                        EssentialGraphsState.Outdated -> OutdatedErrorScreen(
                            modifier = Modifier.padding(bottom = bottomContentPadding).fillMaxSize(),
                            onTryAgainClick = onTryAgainClick
                        )

                        EssentialGraphsState.NoSelectedPlace -> NoSelectedPlaceErrorScreen(
                            modifier = Modifier.padding(bottom = bottomContentPadding).fillMaxSize(),
                            onSelectPlaceClick = onSelectPlaceClick
                        )
                    }
                }
            }
        }
    }
}
'''
start = s.index("@OptIn(ExperimentalMaterial3Api::class)\n@Composable\nfun EssentialGraphsScreen(")
end = s.index("@Composable\nprivate fun Pager(")
s = s[:start] + NEW_MAIN + "\n" + s[end:]
ok("Screen: main function rewritten")

NEW_PAGER = '''@Composable
private fun Pager(
    state: EssentialGraphsState.Success,
    initialDay: LocalDate?,
    metric: GraphMetric?,
    pageContentPadding: PaddingValues,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        val summaries = state.tempGraphSummaries
        val tempGraphs = state.tempGraphs
        val dates = remember(summaries) { summaries.map { it.day } }
        val pagerState = rememberPagerState(initialPage = initialDay?.let { dates.indexOf(it) } ?: 0) { summaries.size }
        val pagerPage by remember { derivedStateOf { pagerState.currentPage } }
        val scope = rememberCoroutineScope()
        GraphsPagerIndicator(
            state = dates,
            selected = pagerPage,
            onClick = {
                scope.launch {
                    pagerState.animateScrollToPage(dates.indexOf(it))
                }
            },
            modifier = Modifier.fillMaxWidth()
        )

        var itemIndex by remember { mutableIntStateOf(0) }
        var itemScrollOffset by remember { mutableIntStateOf(0) }
        HorizontalPager(state = pagerState) { page ->
            val listState = rememberLazyListState()
            LaunchedEffect(itemIndex, itemScrollOffset, page, pagerPage) {
                if (page != pagerPage) {
                    listState.scrollToItem(itemIndex, itemScrollOffset)
                }
            }
            LaunchedEffect(listState) {
                snapshotFlow { listState.firstVisibleItemIndex }
                    .distinctUntilChanged()
                    .collect {
                        if (page == pagerPage) {
                            itemIndex = it
                        }
                    }
            }
            LaunchedEffect(listState) {
                snapshotFlow { listState.firstVisibleItemScrollOffset }
                    .distinctUntilChanged()
                    .collect {
                        if (page == pagerPage) {
                            itemScrollOffset = it
                        }
                    }
            }
            EssentialGraphPage(
                listState = listState,
                contentPadding = pageContentPadding,
                metric = metric,
                now = tempGraphs.now,
                summary = summaries[page],
                temperatureGraph = tempGraphs.graphs[page],
                minTemp = tempGraphs.min,
                maxTemp = tempGraphs.max,
                temperatureArgs = GraphArgs.rememberDefaultArgs(),
                popGraph = state.popGraphs.graphs[page],
                popArgs = GraphArgs.rememberDefaultArgs(),
                windGraph = state.windGraphs.graphs[page],
                windMax = state.windGraphs.max,
                uvIndexGraph = state.uvIndexGraphs.graphs[page],
                uvIndexMax = state.uvIndexGraphs.max,
                precipGraph = state.precipGraphs.graphs[page],
                precipMax = state.precipGraphs.max,
                precipArgs = GraphArgs.rememberDefaultArgs(),
                precipitationTotal = state.precipTotals[page]
            )
        }
    }
}
'''
start = s.index("@Composable\nprivate fun Pager(")
end = s.index("@Composable\nprivate fun EssentialGraphsLoadingIndicator(")
s = s[:start] + NEW_PAGER + "\n" + s[end:]
ok("Screen: Pager rewritten (metric threaded)")
open(p, "w").write(s)

# ---------- 5. EssentialGraphPage.kt ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphPage.kt"
s = open(p).read()

NEW_PAGE = '''@Composable
fun EssentialGraphPage(
    listState: LazyListState,
    contentPadding: PaddingValues,
    now: Instant,
    metric: GraphMetric?,
    summary: TemperatureGraphSummary,
    temperatureGraph: TemperatureGraph,
    minTemp: Temperature,
    maxTemp: Temperature,
    temperatureArgs: GraphArgs,
    popGraph: PopGraph,
    popArgs: GraphArgs,
    windGraph: WindGraph,
    windMax: WindSpeed,
    uvIndexGraph: UvIndexGraph,
    uvIndexMax: UvIndex,
    precipGraph: PrecipitationGraph,
    precipArgs: GraphArgs,
    precipMax: MixedPrecipitation,
    precipitationTotal: PrecipitationTotal
) {
    LazyColumn(
        state = listState,
        verticalArrangement = Arrangement.spacedBy(verticalSpacing),
        contentPadding = contentPadding,
        modifier = Modifier.fillMaxSize()
    ) {
        if (metric == null || metric == GraphMetric.Temperature) {
            item {
                TemperatureGraphSummary(
                    state = summary,
                    modifier = Modifier.fillMaxWidth()
                )
            }
            item {
                TemperatureGraph(
                    now = now,
                    points = temperatureGraph.points,
                    min = minTemp,
                    max = maxTemp,
                    args = temperatureArgs,
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(graphAspectRatio)
                        .border(
                            width = Dp.Hairline,
                            shape = MaterialTheme.shapes.large,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        .clip(MaterialTheme.shapes.large)
                )
            }
        }
        if (metric == null || metric == GraphMetric.UvIndex) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_uv_index))
                    UvIndexGraph(
                        state = uvIndexGraph,
                        max = uvIndexMax,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
        }
        if (metric == null || metric == GraphMetric.Wind) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_wind))
                    WindGraph(
                        state = windGraph,
                        max = windMax,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
        }
        if (metric == null || metric == GraphMetric.Pop) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_pop))
                    PopGraph(
                        now = now,
                        points = popGraph.points,
                        args = popArgs,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
        }
        if (metric == null || metric == GraphMetric.Precipitation) {
            item {
                Column(verticalArrangement = Arrangement.spacedBy(graphLabelSpacing)) {
                    GraphScreenSectionLabel(stringResource(R.string.cond_screen_precip))
                    PrecipitationGraph(
                        now = now,
                        points = precipGraph.points,
                        max = precipMax,
                        args = precipArgs,
                        modifier = Modifier
                            .fillMaxWidth()
                            .aspectRatio(graphAspectRatio)
                            .border(
                                width = Dp.Hairline,
                                shape = MaterialTheme.shapes.large,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                            .clip(MaterialTheme.shapes.large)
                    )
                }
            }
            item {
                when (precipitationTotal) {
                    is PrecipitationTotal.OtherDay -> PrecipitationBullets(
                        state = precipitationTotal.total,
                        modifier = Modifier.fillMaxWidth()
                    )

                    is PrecipitationTotal.Today -> TodayPrecipitationBullets(
                        state = precipitationTotal,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }
        }
        item {
            Text(
                text = stringResource(id = R.string.credit_weather),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
'''
start = s.index("@Composable\nfun EssentialGraphPage(")
end = s.index("@Composable\nfun EssentialGraphPageLoadingIndicator(")
s = s[:start] + NEW_PAGE + "\n" + s[end:]
ok("Page: rewritten, metric-gated")
open(p, "w").write(s)

# ---------- 6. EssentialGraphsViewModel.kt ----------
p = "app/src/main/java/com/davidtakac/bura/graphs/EssentialGraphsViewModel.kt"
s = open(p).read()
anchor = "import com.davidtakac.bura.unexpectederror.UnexpectedErrorSetter"
if anchor in s:
    s = s.replace(anchor, anchor + "\nimport com.davidtakac.bura.theme.SkyBackdrop\nimport com.davidtakac.bura.theme.weatherBackdrop")
    ok("VM: imports added")
else:
    warn("VM: import anchor not found")

s2 = s.replace("""        val windGraphs: WindGraphs,
        val uvIndexGraphs: UvIndexGraphs
    ) : EssentialGraphsState""",
"""        val windGraphs: WindGraphs,
        val uvIndexGraphs: UvIndexGraphs,
        val backdrop: SkyBackdrop
    ) : EssentialGraphsState""")
if s2 != s: ok("VM: Success gains backdrop"); s = s2
else: warn("VM: Success anchor not found")

cm = open("app/src/main/java/com/davidtakac/bura/forecast/parameters/condition/ConditionMoment.kt").read()
cp = open("app/src/main/java/com/davidtakac/bura/forecast/parameters/condition/ConditionPeriod.kt").read()
m_prop = re.search(r"val (cond|condition)\s*:\s*Condition\b", cm)
has_now = re.search(r"val now\b", cp) is not None
if m_prop and has_now:
    accessor = "forecast.condition.now?." + m_prop.group(1)
    computation = (
        "        val condNow = " + accessor + " ?: return EssentialGraphsState.Outdated\n"
        "        val backdrop = weatherBackdrop(condNow, now.hour, golden = false)\n"
    )
    s2 = s.replace(
        "        val uvIndexGraphs = getUvIndexGraphs(now = now, uvIndexPeriod = forecast.uvIndex) ?: return EssentialGraphsState.Outdated\n        return EssentialGraphsState.Success(",
        "        val uvIndexGraphs = getUvIndexGraphs(now = now, uvIndexPeriod = forecast.uvIndex) ?: return EssentialGraphsState.Outdated\n"
        + computation +
        "        return EssentialGraphsState.Success(")
    if s2 != s: ok("VM: backdrop computed via " + accessor); s = s2
    else: warn("VM: computation anchor not found")
else:
    warn("VM: Condition API not discovered (moment prop: %s, period now: %s) - paste ConditionPeriod.kt" % (m_prop.group(1) if m_prop else None, has_now))

s2 = s.replace("""            windGraphs = windGraphs,
            uvIndexGraphs = uvIndexGraphs
        )""",
"""            windGraphs = windGraphs,
            uvIndexGraphs = uvIndexGraphs,
            backdrop = backdrop
        )""")
if s2 != s: ok("VM: Success call carries backdrop"); s = s2
else: warn("VM: Success call anchor not found")
open(p, "w").write(s)

print()
print("\n".join(log))
