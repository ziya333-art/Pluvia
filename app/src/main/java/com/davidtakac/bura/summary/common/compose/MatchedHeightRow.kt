package com.davidtakac.bura.summary.common.compose

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.SubcomposeLayout
import androidx.compose.ui.unit.Constraints
import androidx.compose.ui.unit.Dp

/**
 * A row whose children all match the height of the tallest, measured via
 * subcomposition: the content is composed once to learn its natural heights,
 * then composed again and measured at the shared height. This avoids both
 * intrinsic measurements (unsupported by SubcomposeLayout-based children,
 * such as BoxWithConstraints) and re-measuring the same Measurable (illegal).
 */
@Composable
fun MatchedHeightRow(
    spacing: Dp,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    SubcomposeLayout(modifier) { constraints ->
        if (constraints.maxWidth <= 0) return@SubcomposeLayout layout(0, 0) {}
        val spacingPx = spacing.roundToPx()
        val firstPass = subcompose("natural", content)
        if (firstPass.isEmpty()) return@SubcomposeLayout layout(0, 0) {}
        val n = firstPass.size
        val childWidth = (constraints.maxWidth - spacingPx * (n - 1)) / n
        val naturalConstraints = Constraints(
            minWidth = childWidth,
            maxWidth = childWidth,
            minHeight = 0,
            maxHeight = Constraints.Infinity
        )
        val height = firstPass
            .map { it.measure(naturalConstraints).height }
            .max()
        val secondPass = subcompose("placed", content)
        val placed = secondPass.map {
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
                p.place(x, 0)
                x += p.width + spacingPx
            }
        }
    }
}
