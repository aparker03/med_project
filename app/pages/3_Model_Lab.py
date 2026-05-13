import pandas as pd
import streamlit as st

from utils.charts import (
    feature_importance_chart,
    high_cost_segment_chart,
    lift_chart,
    meps_feature_importance_chart,
    metric_comparison_chart,
    quintile_heatmap,
    regression_metric_chart,
    threshold_chart,
    threshold_error_chart,
)
from utils.data_loader import load_csv
from utils.labels import display_columns, feature_friendly_label, friendly_label
from utils.metrics import format_count, format_number, format_percent
from utils.text_blocks import apply_page_style, callout, caution_note, chart_caption, missing_data_note


st.set_page_config(page_title="Model Lab", page_icon="⚕️", layout="wide")
apply_page_style()

NHIS_COMPARISON_FILES = {
    "Objective 1 model comparison": "nhis_objective1_model_comparison_results.csv",
    "Objective 2 interpretable model results": "nhis_objective2_interpretable_model_results.csv",
}
NHIS_THRESHOLD_FILES = {
    "Objective 1 threshold review": "nhis_objective1_threshold_review.csv",
    "Objective 3 threshold review": "nhis_objective3_threshold_review.csv",
}
NHIS_FEATURE_FILE = "nhis_objective1_random_forest_feature_importance.csv"
NHIS_LIFT_FILE = "nhis_objective3_lift_cost_sensitive_results.csv"

MEPS_COMPARISON_FILES = {
    "Objective 1 model comparison": "meps_objective1_model_comparison_results.csv",
    "Objective 2 interpretable model results": "meps_objective2_interpretable_model_results.csv",
    "Objective 3 robust and skew-aware results": "meps_objective3_robust_skew_aware_results.csv",
}
MEPS_FEATURE_FILE = "meps_objective1_feature_importance.csv"
MEPS_QUINTILE_FILE = "meps_objective1_predicted_actual_quintile.csv"
MEPS_SEGMENT_FILES = {
    "Objective 1 high-cost segment review": "meps_objective1_high_cost_segment_review.csv",
    "Objective 3 high-cost segment review": "meps_objective3_high_cost_segment_review.csv",
}
MEPS_SKEW_FILE = "meps_objective3_robust_skew_aware_results.csv"


def _load_many(files: dict[str, str]) -> dict[str, pd.DataFrame]:
    loaded = {}
    for label, filename in files.items():
        df = load_csv(filename)
        if df is not None and not df.empty:
            loaded[label] = df
    return loaded


def _model_names_from_outputs(files: dict[str, str]) -> list[str]:
    names: set[str] = set()
    for df in _load_many(files).values():
        if "model" in df.columns:
            names.update(df["model"].dropna().astype(str).tolist())
    return sorted(names)


def _model_type_descriptions(model_names: list[str]) -> list[tuple[str, str]]:
    joined = " ".join(model_names).lower()
    descriptions = []
    if any(token in joined for token in ["linear_regression", "lasso", "ridge", "elastic_net"]):
        descriptions.append(
            (
                "Linear and regularized regression",
                "Regression models estimate spending or log-spending with a relatively interpretable structure. Regularization can reduce overfitting but does not remove modeling assumptions.",
            )
        )
    if "logistic" in joined:
        descriptions.append(
            (
                "Logistic regression",
                "Easier to interpret; it looks for linear relationships after preprocessing and weighting or balancing choices.",
            )
        )
    if any(token in joined for token in ["decision_tree", "shallow_tree", "shallow_regression_tree"]):
        descriptions.append(
            (
                "Decision tree",
                "Uses a sequence of splits. It can be easier to explain, but small changes in data can change the tree.",
            )
        )
    if "random_forest" in joined:
        descriptions.append(
            (
                "Random forest",
                "Combines many trees. It can perform well, but its reasoning is less direct than a single simple model.",
            )
        )
    if "gradient" in joined:
        descriptions.append(
            (
                "Gradient boosting",
                "Builds many small models sequentially. It can perform well, but the results need careful interpretation.",
            )
        )
    return descriptions


def _threshold_estimates(row: pd.Series, base: int = 1000) -> dict[str, float | None]:
    predicted_positive = float(row.get("predicted_positive_rate", 0) or 0) * base
    precision = float(row.get("precision", 0) or 0)
    recall = float(row.get("recall", 0) or 0)
    true_positive = precision * predicted_positive
    false_positive = max(predicted_positive - true_positive, 0)
    actual_positive = true_positive / recall if recall > 0 else None
    false_negative = max((actual_positive - true_positive), 0) if actual_positive is not None else None
    return {
        "Flagged rows": predicted_positive,
        "Approx. true positives": true_positive,
        "Approx. false positives": false_positive,
        "Approx. false negatives": false_negative,
    }


def _threshold_estimate_table(df: pd.DataFrame, base: int = 1000) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        rows.append({"threshold": row["threshold"], **_threshold_estimates(row, base=base)})
    return pd.DataFrame(rows)


def _select_metric(columns: list[str], preferred: list[str]) -> str | None:
    for metric in preferred:
        if metric in columns:
            return metric
    return columns[0] if columns else None


def _lower_is_better(metric: str) -> bool:
    return metric not in {"R2", "dollar_R2", "capture_rate", "capture_rate_top20pct", "roc_auc", "average_precision", "precision", "recall", "f1"}


def _format_metric_value(metric: str, value: float) -> str:
    if metric in {"R2", "dollar_R2", "capture_rate", "capture_rate_top20pct", "roc_auc", "average_precision", "precision", "recall", "f1", "precision_050", "recall_050", "f1_050"}:
        return format_percent(value)
    if "MAE" in metric or "RMSE" in metric:
        return f"${value:,.0f}" if "log_" not in metric else format_number(value)
    return format_number(value)


def _render_model_descriptions(files: dict[str, str], context: str) -> None:
    model_names = _model_names_from_outputs(files)
    if not model_names:
        return
    descriptions = _model_type_descriptions(model_names)
    if descriptions:
        with st.expander(f"Model types represented in the saved {context} outputs", expanded=True):
            for title, body in descriptions:
                st.markdown(f"**{title}.** {body}")


def render_nhis_lab() -> None:
    st.markdown(
        """
The NHIS model outputs estimate whether a row belongs to the target class for a cost-related mental health care barrier.
The saved files can help compare tradeoffs, but they do not prove cause and effect and should not be used as individual risk labels.
"""
    )
    _render_model_descriptions({**NHIS_COMPARISON_FILES, "Objective 3 lift and cost-sensitive results": NHIS_LIFT_FILE}, "NHIS")
    caution_note(
        "Use the NHIS Model Lab as an aggregate decision-support learning tool. It should not guide individual care, coverage, outreach, or eligibility decisions."
    )

    tab_compare, tab_features, tab_thresholds, tab_lift, tab_reading = st.tabs(
        ["Model comparison", "Feature importance", "Threshold tradeoffs", "Lift and cost-sensitive review", "Reading NHIS results carefully"]
    )

    with tab_compare:
        comparison_files = {**NHIS_COMPARISON_FILES, "Objective 3 lift and cost-sensitive results": NHIS_LIFT_FILE}
        selected_label = st.selectbox("Saved comparison file", list(comparison_files.keys()), key="nhis_compare_file")
        df = load_csv(comparison_files[selected_label])
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{comparison_files[selected_label]}"))
        else:
            metric_cols = [col for col in ["roc_auc", "average_precision", "precision", "recall", "f1", "precision_050", "recall_050", "f1_050"] if col in df.columns]
            default_metric = _select_metric(metric_cols, ["roc_auc", "average_precision", "recall", "precision", "f1"])
            left, middle, right = st.columns(3)
            left.metric("Rows in file", format_count(len(df)))
            middle.metric("Saved models", format_count(df["model"].nunique()) if "model" in df.columns else "Unknown")
            if default_metric and "model" in df.columns:
                selected_metric = st.selectbox("Metric to compare", metric_cols, index=metric_cols.index(default_metric), format_func=friendly_label, key="nhis_metric")
                strongest = df.sort_values(selected_metric, ascending=False).iloc[0]
                right.metric(f"Highest {friendly_label(selected_metric)}", format_percent(strongest[selected_metric]), strongest["model"])
                callout(
                    "Careful comparison",
                    f"`{strongest['model']}` is highest on {friendly_label(selected_metric)} in this saved file. "
                    "That does not make it best for every practical or ethical use. Recall may matter more for broad screening review, while precision may matter more when over-flagging is a concern.",
                )
                st.plotly_chart(metric_comparison_chart(df, selected_metric), use_container_width=True)
                chart_caption("Longer bars mean higher values for the selected metric. Compare several metrics before choosing a modeling direction.")
            else:
                right.metric("Comparable metrics", "Not found")
                st.info("No standard model metric columns were found for charting.")
            with st.expander("Saved comparison table"):
                st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_features:
        df = load_csv(NHIS_FEATURE_FILE)
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{NHIS_FEATURE_FILE}"))
        elif not {"feature", "importance"}.issubset(df.columns):
            st.error("The feature-importance file is present, but it does not contain the expected `feature` and `importance` columns.")
            st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
        else:
            top_n = st.slider("Number of features to show", min_value=5, max_value=min(25, len(df)), value=min(20, len(df)), key="nhis_feature_n")
            sorted_features = df.sort_values("importance", ascending=False)
            st.plotly_chart(feature_importance_chart(sorted_features, top_n=top_n), use_container_width=True)
            chart_caption("Importance describes how the saved model used a feature. It is not evidence that the feature caused the outcome.")
            feature_table = sorted_features.head(top_n).copy()
            feature_table.insert(0, "Plain-language feature", feature_table["feature"].apply(feature_friendly_label))
            feature_table = feature_table.rename(columns={"feature": "Technical feature name", "importance": "Importance"})
            st.dataframe(feature_table, use_container_width=True, hide_index=True)

    with tab_thresholds:
        selected_label = st.selectbox("Saved threshold file", list(NHIS_THRESHOLD_FILES.keys()), key="nhis_threshold_file")
        df = load_csv(NHIS_THRESHOLD_FILES[selected_label])
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{NHIS_THRESHOLD_FILES[selected_label]}"))
        elif "threshold" not in df.columns:
            st.error("The threshold file is present, but it does not contain the expected `threshold` column.")
            st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
        else:
            thresholds = [float(value) for value in df["threshold"].tolist()]
            selected_threshold = st.select_slider("Review threshold", options=thresholds, value=thresholds[-1], key="nhis_threshold")
            selected_row = df.loc[df["threshold"].astype(float) == float(selected_threshold)].iloc[0]
            st.plotly_chart(threshold_chart(df), use_container_width=True)
            chart_caption("Each line shows how a saved metric changes as the decision threshold changes. Lower thresholds usually flag more rows.")
            metric_cols = st.columns(5)
            metric_cols[0].metric("Threshold", format_number(selected_row["threshold"]))
            for index, metric in enumerate(["precision", "recall", "f1", "predicted_positive_rate"], start=1):
                if metric in df.columns:
                    metric_cols[index].metric(friendly_label(metric), format_percent(selected_row[metric]))
            if {"precision", "recall", "predicted_positive_rate"}.issubset(df.columns):
                all_estimates_df = _threshold_estimate_table(df)
                st.plotly_chart(threshold_error_chart(all_estimates_df), use_container_width=True)
                chart_caption("False-positive and false-negative counts are derived from saved threshold metrics and shown per 1,000 evaluated rows.")
            callout(
                "Threshold tradeoff",
                "Lowering a threshold may catch more rows with the measured cost barrier, but it can also increase false positives. Raising a threshold may reduce over-flagging, but it can increase false negatives.",
            )
            with st.expander("Saved threshold table"):
                st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_lift:
        df = load_csv(NHIS_LIFT_FILE)
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{NHIS_LIFT_FILE}"))
        else:
            st.plotly_chart(lift_chart(df), use_container_width=True)
            chart_caption("Lift summarizes how concentrated the measured target is among the highest-ranked rows compared with the overall rate.")
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_reading:
        st.subheader("Plain-language metric guide")
        st.markdown(
            """
**Precision**: among rows the model flags, the share that have the measured target.

**Recall**: among rows with the measured target, the share the model flags.

**F1 score**: a compact balance between precision and recall. It is helpful, but it can hide the practical cost of each kind of error.

**ROC AUC**: how well the model ranks rows with the target above rows without it across many thresholds.

**Average precision**: a precision-recall summary that is often useful when the target is uncommon.
"""
        )
        caution_note("These metrics describe saved model behavior on evaluation data. They do not identify who truly needs care or who deserves services.")


def render_meps_lab() -> None:
    st.markdown(
        """
MEPS model outputs focus on healthcare expenditure outcomes. These outcomes are often skewed because many people have
low or zero costs and a smaller group has very high costs. Regression results need careful review because high-cost
cases can strongly affect model behavior.
"""
    )
    _render_model_descriptions(MEPS_COMPARISON_FILES, "MEPS")
    caution_note(
        "MEPS models are learning tools for aggregate review. They should not be used to make individual care, coverage, financial hardship, or eligibility decisions."
    )

    tab_compare, tab_features, tab_quintile, tab_segments, tab_skew, tab_reading = st.tabs(
        [
            "Model comparison",
            "Feature importance",
            "Predicted vs actual spending groups",
            "High-cost segment review",
            "Robust/skew-aware results",
            "Reading MEPS results carefully",
        ]
    )

    with tab_compare:
        selected_label = st.selectbox("Saved MEPS comparison file", list(MEPS_COMPARISON_FILES.keys()), key="meps_compare_file")
        df = load_csv(MEPS_COMPARISON_FILES[selected_label])
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{MEPS_COMPARISON_FILES[selected_label]}"))
        else:
            metric_cols = [col for col in ["MAE", "RMSE", "R2", "high_cost_MAE", "dollar_MAE", "dollar_RMSE", "dollar_R2", "capture_rate_top20pct", "log_MAE", "log_RMSE"] if col in df.columns]
            default_metric = _select_metric(metric_cols, ["MAE", "dollar_MAE", "RMSE", "dollar_RMSE", "high_cost_MAE", "capture_rate_top20pct", "R2"])
            left, middle, right = st.columns(3)
            left.metric("Rows in file", format_count(len(df)))
            middle.metric("Saved models", format_count(df["model"].nunique()) if "model" in df.columns else "Unknown")
            if default_metric and "model" in df.columns:
                selected_metric = st.selectbox("Metric to compare", metric_cols, index=metric_cols.index(default_metric), format_func=friendly_label, key="meps_metric")
                lower_is_better = _lower_is_better(selected_metric)
                strongest = df.sort_values(selected_metric, ascending=lower_is_better).iloc[0]
                right.metric(f"Stronger on {friendly_label(selected_metric)}", _format_metric_value(selected_metric, strongest[selected_metric]), strongest["model"])
                callout(
                    "Careful comparison",
                    f"`{strongest['model']}` is strongest on {friendly_label(selected_metric)} in this saved file. "
                    "That does not make it the best model for every purpose. High-cost cases and skewed spending can change how metrics behave.",
                )
                st.plotly_chart(regression_metric_chart(df, selected_metric, lower_is_better=lower_is_better), use_container_width=True)
                chart_caption("Lower is better for MAE and RMSE. Higher is better for R-squared and capture-rate metrics.")
            else:
                right.metric("Comparable metrics", "Not found")
                st.info("No standard MEPS model metric columns were found for charting.")
            with st.expander("Saved MEPS comparison table"):
                st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_features:
        df = load_csv(MEPS_FEATURE_FILE)
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{MEPS_FEATURE_FILE}"))
        elif "feature" not in df.columns:
            st.error("The MEPS feature file is present, but it does not contain a `feature` column.")
            st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
        else:
            top_n = st.slider("Number of features to show", min_value=5, max_value=min(25, len(df)), value=min(20, len(df)), key="meps_feature_n")
            st.plotly_chart(meps_feature_importance_chart(df, top_n=top_n), use_container_width=True)
            chart_caption("Feature effects or importance values show what the saved model used. They do not prove that a feature caused spending.")
            value_col = "abs_coef" if "abs_coef" in df.columns else "importance" if "importance" in df.columns else None
            if value_col:
                feature_table = df.sort_values(value_col, ascending=False).head(top_n).copy()
                feature_table.insert(0, "Plain-language feature", feature_table["feature"].apply(feature_friendly_label))
                st.dataframe(display_columns(feature_table), use_container_width=True, hide_index=True)

    with tab_quintile:
        df = load_csv(MEPS_QUINTILE_FILE)
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{MEPS_QUINTILE_FILE}"))
        else:
            st.plotly_chart(quintile_heatmap(df), use_container_width=True)
            chart_caption("Cells show how often rows fall into each actual and predicted spending group. A stronger ranking pattern appears closer to the diagonal.")
            callout("Spending groups", "This review helps inspect model ranking behavior across spending groups. It does not determine individual financial hardship.")
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_segments:
        selected_label = st.selectbox("Saved high-cost segment file", list(MEPS_SEGMENT_FILES.keys()), key="meps_segment_file")
        df = load_csv(MEPS_SEGMENT_FILES[selected_label])
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{MEPS_SEGMENT_FILES[selected_label]}"))
        elif "segment" not in df.columns:
            st.error("The segment review file is present, but it does not contain a `segment` column.")
            st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
        else:
            st.plotly_chart(high_cost_segment_chart(df, selected_label), use_container_width=True)
            chart_caption("High-cost segment review inspects model behavior in the upper end of healthcare spending, where errors can be large.")
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_skew:
        df = load_csv(MEPS_SKEW_FILE)
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{MEPS_SKEW_FILE}"))
        else:
            metric_cols = [col for col in ["dollar_MAE", "dollar_RMSE", "high_cost_MAE", "capture_rate_top20pct", "log_MAE", "log_RMSE", "dollar_R2"] if col in df.columns]
            selected_metric = st.selectbox("Robust/skew-aware metric", metric_cols, index=0, format_func=friendly_label, key="meps_skew_metric") if metric_cols else None
            if selected_metric:
                st.plotly_chart(regression_metric_chart(df, selected_metric, lower_is_better=_lower_is_better(selected_metric)), use_container_width=True)
                chart_caption("Skew-aware results compare log-scale and dollar-scale behavior. Read both views before judging model usefulness.")
            callout(
                "Skew-aware review",
                "High-cost cases can dominate dollar-scale errors. Log-scale and robust checks help show whether model behavior changes under another framing.",
            )
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

    with tab_reading:
        st.subheader("Reading MEPS results carefully")
        st.markdown(
            """
**Total spending** is often skewed. A small number of very high-cost rows can strongly affect dollar-scale metrics.

**MAE** is the average absolute dollar error. It is usually easier to read than RMSE.

**RMSE** penalizes larger errors more heavily, so it can be strongly affected by high-cost cases.

**R-squared** summarizes explained variation, but it can look modest for noisy expenditure outcomes.

**High-cost segment review** checks how models behave in the upper part of the spending distribution.

**Feature importance** and coefficient size do not prove causality. They describe model behavior in the saved analysis.
"""
        )
        caution_note("MEPS model outputs should not be used to decide individual care, coverage, benefits, or eligibility.")


st.title("Model Lab")
st.caption("A review space for saved NHIS and MEPS model artifacts. The page reads CSV outputs only and does not retrain models.")

dataset = st.radio("Choose model output family", ["NHIS model outputs", "MEPS model outputs"], horizontal=True)

if dataset == "NHIS model outputs":
    render_nhis_lab()
else:
    render_meps_lab()
