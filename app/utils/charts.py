import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.labels import format_group_value, friendly_label


COLOR_SEQUENCE = ["#38bdf8", "#2dd4bf", "#fbbf24", "#fb7185", "#a78bfa", "#f97316"]


def _finish_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#111827",
        font={"size": 15, "color": "#f8fafc"},
        title={"font": {"size": 20, "color": "#ffffff"}},
        legend={"font": {"size": 14}, "orientation": "h", "y": -0.18},
        xaxis={"title_font": {"size": 16}, "tickfont": {"size": 13}, "gridcolor": "#334155"},
        yaxis={"title_font": {"size": 16}, "tickfont": {"size": 13}, "gridcolor": "#334155"},
    )
    return fig


def _clean_feature_name(feature: str) -> str:
    cleaned = str(feature).replace("categorical__", "").replace("numeric__", "")
    return friendly_label(cleaned)


def bar_rate_chart(df: pd.DataFrame, title: str) -> go.Figure:
    chart_df = df.copy()
    hover_df = chart_df.reindex(columns=["unweighted_n", "unweighted_rate"])
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=chart_df["weighted_rate"],
            y=chart_df["group_display"],
            orientation="h",
            name="Survey-weighted rate",
            marker_color=COLOR_SEQUENCE[0],
            text=[f"{value:.1%}" for value in chart_df["weighted_rate"]],
            textposition="auto",
            customdata=hover_df,
            hovertemplate=(
                "<b>%{y}</b><br>Survey-weighted rate: %{x:.1%}"
                + ("<br>Raw sample count: %{customdata[0]:,.0f}" if "unweighted_n" in chart_df.columns else "")
                + ("<br>Raw sample rate: %{customdata[1]:.1%}" if "unweighted_rate" in chart_df.columns else "")
                + "<extra></extra>"
            ),
        )
    )
    if "unweighted_rate" in chart_df.columns:
        fig.add_trace(
            go.Scatter(
                x=chart_df["unweighted_rate"],
                y=chart_df["group_display"],
                mode="markers",
                name="Raw sample rate",
                marker={"color": COLOR_SEQUENCE[2], "size": 11, "line": {"color": "#111827", "width": 1}},
            )
        )
    x_max = min(max(float(chart_df["weighted_rate"].max()) * 1.2, 0.05), 1)
    fig.update_layout(
        title=title,
        xaxis_title="Mental health cost-barrier rate",
        yaxis_title="",
        xaxis_tickformat=".0%",
        xaxis_range=[0, x_max],
        legend_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 70},
        height=max(430, 72 * len(chart_df)),
    )
    fig.update_yaxes(autorange="reversed")
    return _finish_figure(fig)


def distribution_chart(df: pd.DataFrame, column: str) -> go.Figure:
    if pd.api.types.is_numeric_dtype(df[column]) and df[column].nunique(dropna=True) > 12:
        fig = px.histogram(df, x=column, nbins=30, color_discrete_sequence=[COLOR_SEQUENCE[0]])
        fig.update_layout(yaxis_title="Rows")
    else:
        display_values = df[column].apply(lambda value: format_group_value(column, value))
        counts = display_values.value_counts().reset_index()
        counts.columns = [friendly_label(column), "rows"]
        fig = px.bar(
            counts,
            x=friendly_label(column),
            y="rows",
            color_discrete_sequence=[COLOR_SEQUENCE[0]],
            text="rows",
        )
    fig.update_layout(
        title=friendly_label(column),
        xaxis_title=friendly_label(column),
        yaxis_title="Rows",
        margin={"l": 20, "r": 20, "t": 60, "b": 40},
        showlegend=False,
    )
    return _finish_figure(fig)


def metric_comparison_chart(df: pd.DataFrame, metric: str) -> go.Figure:
    chart_df = df.sort_values(metric, ascending=True).copy()
    label_cols = [col for col in ["version", "objective", "model"] if col in chart_df.columns]
    chart_df["display_name"] = chart_df[label_cols].astype(str).agg(" - ".join, axis=1)
    fig = px.bar(
        chart_df,
        x=metric,
        y="display_name",
        orientation="h",
        color="model" if "model" in chart_df.columns else None,
        color_discrete_sequence=COLOR_SEQUENCE,
        text=metric,
    )
    fig.update_traces(texttemplate="%{x:.3f}", textposition="auto")
    fig.update_layout(
        title=friendly_label(metric),
        xaxis_title=friendly_label(metric),
        yaxis_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 40},
        showlegend=False,
    )
    return _finish_figure(fig)


def regression_metric_chart(df: pd.DataFrame, metric: str, lower_is_better: bool = True) -> go.Figure:
    if metric not in df.columns or "model" not in df.columns:
        return _finish_figure(go.Figure())

    chart_df = df.sort_values(metric, ascending=lower_is_better).copy()
    label_cols = [col for col in ["objective", "version", "model"] if col in chart_df.columns]
    chart_df["display_name"] = chart_df[label_cols].astype(str).agg(" - ".join, axis=1)
    chart_df = chart_df.sort_values(metric, ascending=not lower_is_better)
    fig = px.bar(
        chart_df,
        x=metric,
        y="display_name",
        orientation="h",
        color="model",
        color_discrete_sequence=COLOR_SEQUENCE,
        text=metric,
    )
    text_template = "%{x:,.0f}" if metric.upper() in {"MAE", "RMSE", "HIGH_COST_MAE"} or "MAE" in metric or "RMSE" in metric else "%{x:.3f}"
    fig.update_traces(texttemplate=text_template, textposition="auto")
    fig.update_layout(
        title=friendly_label(metric),
        xaxis_title=friendly_label(metric),
        yaxis_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 60},
        showlegend=False,
        height=max(440, 58 * len(chart_df)),
    )
    return _finish_figure(fig)


def feature_importance_chart(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    chart_df = df.sort_values("importance", ascending=False).head(top_n).copy()
    chart_df["feature_label"] = chart_df["feature"].apply(_clean_feature_name)
    chart_df = chart_df.sort_values("importance", ascending=True)
    fig = px.bar(
        chart_df,
        x="importance",
        y="feature_label",
        orientation="h",
        color_discrete_sequence=[COLOR_SEQUENCE[2]],
        text="importance",
    )
    fig.update_traces(texttemplate="%{x:.3f}", textposition="auto")
    fig.update_layout(
        title="Top feature importance values",
        xaxis_title="Importance",
        yaxis_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 40},
    )
    return _finish_figure(fig)


def meps_feature_importance_chart(df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    value_col = "abs_coef" if "abs_coef" in df.columns else "importance" if "importance" in df.columns else None
    feature_col = "feature" if "feature" in df.columns else None
    if value_col is None or feature_col is None:
        return _finish_figure(go.Figure())

    chart_df = df.sort_values(value_col, ascending=False).head(top_n).copy()
    chart_df["feature_label"] = chart_df[feature_col].apply(_clean_feature_name)
    chart_df = chart_df.sort_values(value_col, ascending=True)
    fig = px.bar(
        chart_df,
        x=value_col,
        y="feature_label",
        orientation="h",
        color_discrete_sequence=[COLOR_SEQUENCE[2]],
        text=value_col,
    )
    fig.update_traces(texttemplate="%{x:,.0f}", textposition="auto")
    fig.update_layout(
        title="Largest saved feature effects or importance values",
        xaxis_title=friendly_label(value_col),
        yaxis_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 40},
        height=max(520, 34 * top_n),
    )
    return _finish_figure(fig)


def threshold_chart(df: pd.DataFrame) -> go.Figure:
    metric_cols = [col for col in ["precision", "recall", "f1", "predicted_positive_rate"] if col in df.columns]
    fig = go.Figure()
    for index, col in enumerate(metric_cols):
        fig.add_trace(
            go.Scatter(
                x=df["threshold"],
                y=df[col],
                mode="lines+markers",
                name=friendly_label(col),
                line={"color": COLOR_SEQUENCE[index % len(COLOR_SEQUENCE)]},
            )
        )
    fig.update_layout(
        title="Threshold tradeoffs",
        xaxis_title="Threshold",
        yaxis_title="Metric value",
        yaxis_tickformat=".0%",
        legend_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 80},
    )
    return _finish_figure(fig)


def high_cost_segment_chart(df: pd.DataFrame, title: str) -> go.Figure:
    metric_cols = [col for col in ["MAE", "RMSE"] if col in df.columns]
    if not metric_cols:
        metric_cols = [col for col in ["capture_rate"] if col in df.columns]
    if not metric_cols or "segment" not in df.columns:
        return _finish_figure(go.Figure())

    chart_df = df[["segment", *metric_cols]].melt(id_vars="segment", var_name="Metric", value_name="Value")
    fig = px.bar(
        chart_df,
        x="segment",
        y="Value",
        color="Metric",
        barmode="group",
        color_discrete_sequence=COLOR_SEQUENCE,
        text="Value",
    )
    fig.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
    fig.update_layout(
        title=title,
        xaxis_title="High-cost segment",
        yaxis_title="Metric value",
        margin={"l": 20, "r": 20, "t": 60, "b": 100},
        height=520,
    )
    return _finish_figure(fig)


def quintile_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _finish_figure(go.Figure())

    index_col = df.columns[0]
    matrix = df.set_index(index_col)
    fig = px.imshow(
        matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale=["#111827", "#2563eb", "#fbbf24"],
    )
    fig.update_layout(
        title="Predicted spending group by actual spending group",
        xaxis_title="Predicted spending group",
        yaxis_title="Actual spending group",
        margin={"l": 20, "r": 20, "t": 60, "b": 60},
        height=520,
    )
    return _finish_figure(fig)


def spending_distribution_chart(df: pd.DataFrame, column: str = "TOTEXP23") -> go.Figure:
    if column not in df.columns:
        return _finish_figure(go.Figure())

    chart_df = df[[column]].copy()
    fig = px.histogram(chart_df, x=column, nbins=50, color_discrete_sequence=[COLOR_SEQUENCE[0]])
    fig.update_layout(
        title="Distribution of total healthcare spending",
        xaxis_title=friendly_label(column),
        yaxis_title="Rows",
        margin={"l": 20, "r": 20, "t": 60, "b": 60},
        height=470,
    )
    return _finish_figure(fig)


def threshold_error_chart(df: pd.DataFrame) -> go.Figure:
    if not {"threshold", "Approx. false positives", "Approx. false negatives"}.issubset(df.columns):
        return _finish_figure(go.Figure())

    chart_df = df[["threshold", "Approx. false positives", "Approx. false negatives"]].melt(
        id_vars="threshold",
        var_name="Error type",
        value_name="Approximate count per 1,000 evaluated rows",
    )
    fig = px.line(
        chart_df,
        x="threshold",
        y="Approximate count per 1,000 evaluated rows",
        color="Error type",
        markers=True,
        color_discrete_sequence=[COLOR_SEQUENCE[3], COLOR_SEQUENCE[4]],
    )
    fig.update_layout(
        title="Approximate error counts by threshold",
        xaxis_title="Threshold",
        yaxis_title="Approximate count per 1,000 evaluated rows",
        legend_title="",
        margin={"l": 20, "r": 20, "t": 60, "b": 80},
        height=460,
    )
    return _finish_figure(fig)


def lift_chart(df: pd.DataFrame) -> go.Figure:
    lift_cols = [col for col in ["lift_top_10pct", "lift_top_20pct", "lift_top_30pct"] if col in df.columns]
    if not lift_cols or "model" not in df.columns:
        return _finish_figure(go.Figure())

    chart_df = df[["model", *lift_cols]].melt(id_vars="model", var_name="Review group", value_name="Lift")
    chart_df["Review group"] = chart_df["Review group"].replace(
        {
            "lift_top_10pct": "Top 10%",
            "lift_top_20pct": "Top 20%",
            "lift_top_30pct": "Top 30%",
        }
    )
    fig = px.bar(
        chart_df,
        x="model",
        y="Lift",
        color="Review group",
        barmode="group",
        color_discrete_sequence=COLOR_SEQUENCE,
        text="Lift",
    )
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig.update_layout(
        title="Lift in the highest-ranked groups",
        xaxis_title="Saved model",
        yaxis_title="Lift compared with the overall rate",
        margin={"l": 20, "r": 20, "t": 60, "b": 100},
        height=520,
    )
    return _finish_figure(fig)
