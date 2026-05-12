import pandas as pd
import streamlit as st

from utils.charts import (
    feature_importance_chart,
    lift_chart,
    metric_comparison_chart,
    threshold_chart,
    threshold_error_chart,
)
from utils.data_loader import load_csv
from utils.labels import display_columns, feature_friendly_label, friendly_label
from utils.metrics import format_count, format_number, format_percent
from utils.text_blocks import apply_page_style, callout, caution_note, chart_caption, missing_data_note


st.set_page_config(page_title="Model Lab", page_icon="⚕️", layout="wide")
apply_page_style()

COMPARISON_FILES = {
    "Objective 1 model comparison": "nhis_objective1_model_comparison_results.csv",
    "Objective 2 interpretable model results": "nhis_objective2_interpretable_model_results.csv",
}

THRESHOLD_FILES = {
    "Objective 1 threshold review": "nhis_objective1_threshold_review.csv",
    "Objective 3 threshold review": "nhis_objective3_threshold_review.csv",
}

FEATURE_FILE = "nhis_objective1_random_forest_feature_importance.csv"
LIFT_FILE = "nhis_objective3_lift_cost_sensitive_results.csv"


def _load_many(files: dict[str, str]) -> dict[str, pd.DataFrame]:
    loaded = {}
    for label, filename in files.items():
        df = load_csv(filename)
        if df is not None and not df.empty:
            loaded[label] = df
    return loaded


def _model_names_from_outputs() -> list[str]:
    names: set[str] = set()
    for df in [*_load_many(COMPARISON_FILES).values(), load_csv(LIFT_FILE)]:
        if df is not None and not df.empty and "model" in df.columns:
            names.update(df["model"].dropna().astype(str).tolist())
    return sorted(names)


def _model_type_descriptions(model_names: list[str]) -> list[tuple[str, str]]:
    joined = " ".join(model_names).lower()
    descriptions = []
    if "logistic" in joined:
        descriptions.append(
            (
                "Logistic regression",
                "Easier to interpret; it looks for linear relationships after preprocessing and weighting or balancing choices.",
            )
        )
    if "decision_tree" in joined or "shallow_tree" in joined:
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
        estimates = _threshold_estimates(row, base=base)
        rows.append({"threshold": row["threshold"], **estimates})
    return pd.DataFrame(rows)


def _select_metric(columns: list[str]) -> str | None:
    preferred = ["roc_auc", "average_precision", "recall", "precision", "f1", "recall_050", "precision_050", "f1_050"]
    for metric in preferred:
        if metric in columns:
            return metric
    return columns[0] if columns else None


st.title("Model Lab")
st.caption("A review space for saved model artifacts. The page reads CSV outputs only and does not retrain models.")

model_names = _model_names_from_outputs()

st.markdown(
    """
The saved models estimate the probability that a row belongs to the target class based on patterns in the training data.
In this project, the target is a cost-related mental health care barrier. These outputs can help compare modeling
tradeoffs, but they do not prove cause and effect and should not be used as clinical tools, eligibility tools, or
individual risk labels.
"""
)

if model_names:
    descriptions = _model_type_descriptions(model_names)
    if descriptions:
        with st.expander("Model types represented in the saved outputs", expanded=True):
            for title, body in descriptions:
                st.markdown(f"**{title}.** {body}")

caution_note(
    "Use this page as a decision-support learning tool for aggregate review. It should not be used to decide who deserves care, coverage, outreach, or services."
)

tab_compare, tab_features, tab_thresholds, tab_lift, tab_reading = st.tabs(
    [
        "Model comparison",
        "Feature importance",
        "Threshold tradeoffs",
        "Lift and cost-sensitive review",
        "Reading the results carefully",
    ]
)

with tab_compare:
    comparison_files = {**COMPARISON_FILES, "Objective 3 lift and cost-sensitive results": LIFT_FILE}
    selected_label = st.selectbox("Saved comparison file", list(comparison_files.keys()))
    df = load_csv(comparison_files[selected_label])

    if df is None or df.empty:
        st.warning(missing_data_note(f"data/processed/{comparison_files[selected_label]}"))
    else:
        metric_cols = [
            col
            for col in [
                "roc_auc",
                "average_precision",
                "precision",
                "recall",
                "f1",
                "precision_050",
                "recall_050",
                "f1_050",
            ]
            if col in df.columns
        ]
        default_metric = _select_metric(metric_cols)

        left, middle, right = st.columns(3)
        left.metric("Rows in file", format_count(len(df)))
        middle.metric("Saved models", format_count(df["model"].nunique()) if "model" in df.columns else "Unknown")
        if default_metric and "model" in df.columns:
            selected_metric = st.selectbox("Metric to compare", metric_cols, index=metric_cols.index(default_metric), format_func=friendly_label)
            strongest = df.sort_values(selected_metric, ascending=False).iloc[0]
            right.metric(f"Highest {friendly_label(selected_metric)}", format_percent(strongest[selected_metric]), strongest["model"])
            callout(
                "Careful comparison",
                f"`{strongest['model']}` is highest on {friendly_label(selected_metric)} in this saved file. "
                "That does not make it best for every practical or ethical use. If the goal is screening possible barriers, recall may matter more. "
                "If the goal is avoiding over-flagging, precision may matter more.",
            )
            st.plotly_chart(metric_comparison_chart(df, selected_metric), use_container_width=True)
            chart_caption(
                "Longer bars mean higher values for the selected metric. Compare several metrics before choosing a modeling direction."
            )
        else:
            right.metric("Comparable metrics", "Not found")
            st.info("No standard model metric columns were found for charting.")

        with st.expander("Saved comparison table"):
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

with tab_features:
    df = load_csv(FEATURE_FILE)
    if df is None or df.empty:
        st.warning(missing_data_note(f"data/processed/{FEATURE_FILE}"))
    elif not {"feature", "importance"}.issubset(df.columns):
        st.error("The feature-importance file is present, but it does not contain the expected `feature` and `importance` columns.")
        st.write("Available columns:")
        st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
    else:
        top_n = st.slider("Number of features to show", min_value=5, max_value=min(25, len(df)), value=min(20, len(df)))
        sorted_features = df.sort_values("importance", ascending=False)
        st.plotly_chart(feature_importance_chart(sorted_features, top_n=top_n), use_container_width=True)
        chart_caption(
            "The chart shows the largest saved importance values. Importance describes how the model used a feature; it is not evidence that the feature caused the outcome."
        )
        caution_note("Feature importance is not causality. It can reflect correlations, coding choices, missingness patterns, and interactions with other variables.")

        feature_table = sorted_features.head(top_n).copy()
        feature_table.insert(0, "Plain-language feature", feature_table["feature"].apply(feature_friendly_label))
        feature_table = feature_table.rename(columns={"feature": "Technical feature name", "importance": "Importance"})
        with st.expander("Feature table with technical names", expanded=True):
            st.dataframe(feature_table, use_container_width=True, hide_index=True)

with tab_thresholds:
    selected_label = st.selectbox("Saved threshold file", list(THRESHOLD_FILES.keys()))
    df = load_csv(THRESHOLD_FILES[selected_label])

    if df is None or df.empty:
        st.warning(missing_data_note(f"data/processed/{THRESHOLD_FILES[selected_label]}"))
    elif "threshold" not in df.columns:
        st.error("The threshold file is present, but it does not contain the expected `threshold` column.")
        st.write("Available columns:")
        st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
    else:
        thresholds = [float(value) for value in df["threshold"].tolist()]
        selected_threshold = st.select_slider("Review threshold", options=thresholds, value=thresholds[-1])
        selected_row = df.loc[df["threshold"].astype(float) == float(selected_threshold)].iloc[0]

        st.plotly_chart(threshold_chart(df), use_container_width=True)
        chart_caption(
            "Each line shows how a saved metric changes as the decision threshold changes. Lower thresholds usually flag more rows."
        )

        metric_cols = st.columns(5)
        metric_cols[0].metric("Threshold", format_number(selected_row["threshold"]))
        if "precision" in df.columns:
            metric_cols[1].metric("Precision", format_percent(selected_row["precision"]))
        if "recall" in df.columns:
            metric_cols[2].metric("Recall", format_percent(selected_row["recall"]))
        if "f1" in df.columns:
            metric_cols[3].metric("F1 score", format_percent(selected_row["f1"]))
        if "predicted_positive_rate" in df.columns:
            metric_cols[4].metric("Rows flagged", format_percent(selected_row["predicted_positive_rate"]))

        if {"precision", "recall", "predicted_positive_rate"}.issubset(df.columns):
            all_estimates_df = _threshold_estimate_table(df)
            estimates = _threshold_estimates(selected_row)
            estimate_df = pd.DataFrame(
                [{"Measure": key, "Approximate count per 1,000 evaluated rows": value} for key, value in estimates.items()]
            )
            st.plotly_chart(threshold_error_chart(all_estimates_df), use_container_width=True)
            chart_caption(
                "These false-positive and false-negative counts are derived from the saved threshold metrics and shown per 1,000 evaluated rows for scale."
            )
            st.dataframe(
                estimate_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Approximate count per 1,000 evaluated rows": st.column_config.NumberColumn(
                        "Approximate count per 1,000 evaluated rows",
                        format="%.1f",
                    )
                },
            )
            with st.expander("Approximate threshold counts per 1,000 rows"):
                st.dataframe(display_columns(all_estimates_df), use_container_width=True, hide_index=True)

        callout(
            "Threshold tradeoff",
            "Lowering a threshold may catch more rows with the measured cost barrier, but it can also increase false positives. "
            "Raising a threshold may reduce over-flagging, but it can increase false negatives.",
        )
        st.markdown(
            """
In this project context, a **false positive** means a row is flagged even though the measured target is not present in the evaluation data.
A **false negative** means the measured target is present but the row is not flagged. These are aggregate validation concepts, not labels
to apply to individual people.
"""
        )

        with st.expander("Saved threshold table"):
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

with tab_lift:
    df = load_csv(LIFT_FILE)
    if df is None or df.empty:
        st.warning(missing_data_note(f"data/processed/{LIFT_FILE}"))
    else:
        st.markdown(
            "Lift summarizes how concentrated the measured target is among the highest-ranked rows compared with the overall rate. "
            "It is useful for reviewing ranking behavior, but it does not say whether a model should be used operationally."
        )
        st.plotly_chart(lift_chart(df), use_container_width=True)
        chart_caption(
            "A lift of 3 means the selected top-ranked group has about three times the measured target rate of the overall evaluation set."
        )
        with st.expander("Saved lift and cost-sensitive table", expanded=True):
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

**False positives**: rows flagged by the model that do not have the measured target in the evaluation data.

**False negatives**: rows that have the measured target in the evaluation data but are not flagged by the model.
"""
    )
    caution_note(
        "These metrics describe saved model behavior on evaluation data. They do not identify who truly needs care, who deserves services, or who should receive benefits."
    )
