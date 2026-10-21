package com.davidtakac.bura.graphs

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
