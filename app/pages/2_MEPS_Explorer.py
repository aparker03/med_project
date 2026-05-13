import pandas as pd
import streamlit as st

from utils.charts import (
    high_cost_segment_chart,
    quintile_heatmap,
    regression_metric_chart,
    spending_distribution_chart,
)
from utils.data_loader import load_csv
from utils.labels import display_columns, friendly_label
from utils.metrics import format_count, format_number
from utils.text_blocks import apply_page_style, callout, caution_note, chart_caption, metric_card, missing_data_note


st.set_page_config(page_title="MEPS Explorer", page_icon="⚕️", layout="wide")
apply_page_style()

MEPS_FILES = {
    "model_ready": "meps_model_ready_v1.csv",
    "model_ready_saq": "meps_model_ready_v1_with_saq.csv",
    "checkpoint": "meps_modeling_checkpoint.csv",
    "objective1_segment": "meps_objective1_high_cost_segment_review.csv",
    "objective3_segment": "meps_objective3_high_cost_segment_review.csv",
    "quintile": "meps_objective1_predicted_actual_quintile.csv",
    "skew": "meps_objective3_robust_skew_aware_results.csv",
}


def _load(name: str) -> pd.DataFrame | None:
    return load_csv(MEPS_FILES[name])


def _best_available_metric(df: pd.DataFrame) -> str | None:
    for metric in ["dollar_MAE", "MAE", "high_cost_MAE", "RMSE", "dollar_RMSE", "capture_rate_top20pct", "R2", "dollar_R2"]:
        if metric in df.columns:
            return metric
    return None


st.title("MEPS Explorer")
st.caption("Healthcare spending, cost burden, high-cost segments, and skew-aware model outputs from saved MEPS CSVs.")

st.markdown(
    """
MEPS complements the NHIS side of the project by focusing more directly on healthcare use, expenditures,
insurance coverage, and cost burden. Spending outcomes need careful handling because many people have low
or zero costs while a smaller group has very high costs.
"""
)

model_df = _load("model_ready")
model_saq_df = _load("model_ready_saq")
checkpoint_df = _load("checkpoint")
skew_df = _load("skew")

rows_value = format_count(len(model_df)) if model_df is not None and not model_df.empty else "File missing"
spending_value = "Not available"
if model_df is not None and not model_df.empty and "TOTEXP23" in model_df.columns:
    spending_value = f"${model_df['TOTEXP23'].median():,.0f}"

models_value = "File missing"
if checkpoint_df is not None and not checkpoint_df.empty and "models_trained" in checkpoint_df.columns:
    models_value = format_count(checkpoint_df["models_trained"].sum())

top20_value = "Not available"
if skew_df is not None and not skew_df.empty and "capture_rate_top20pct" in skew_df.columns:
    top20_value = f"{skew_df['capture_rate_top20pct'].max():.1%}"

card_a, card_b, card_c, card_d = st.columns(4)
with card_a:
    st.markdown(
        metric_card("MEPS rows", rows_value, "Rows in the saved model-ready MEPS file."),
        unsafe_allow_html=True,
    )
with card_b:
    st.markdown(
        metric_card("Median spending", spending_value, "Median total healthcare spending in the model-ready file."),
        unsafe_allow_html=True,
    )
with card_c:
    st.markdown(
        metric_card("Models trained", models_value, "Saved checkpoint count across MEPS modeling objectives."),
        unsafe_allow_html=True,
    )
with card_d:
    st.markdown(
        metric_card("Top 20% capture", top20_value, "Highest saved capture rate for the top predicted spending group."),
        unsafe_allow_html=True,
    )

caution_note(
    "MEPS spending summaries and model outputs are aggregate review tools. They do not determine individual medical need, financial hardship, eligibility, or coverage decisions."
)

tab_overview, tab_segments, tab_quintiles, tab_skew, tab_files = st.tabs(
    [
        "Spending overview",
        "High-cost segments",
        "Predicted vs actual groups",
        "Skew-aware results",
        "File details",
    ]
)

with tab_overview:
    if model_df is None or model_df.empty:
        st.warning(missing_data_note(f"data/processed/{MEPS_FILES['model_ready']}"))
    elif "TOTEXP23" not in model_df.columns:
        st.warning("The MEPS model-ready file is present, but `TOTEXP23` was not found for the spending overview.")
        st.write("Available columns:")
        st.dataframe({"Column": list(model_df.columns)}, use_container_width=True, hide_index=True)
    else:
        left, right = st.columns([2, 1])
        with left:
            st.plotly_chart(spending_distribution_chart(model_df, "TOTEXP23"), use_container_width=True)
            chart_caption(
                "The spending distribution is usually uneven: many rows cluster at lower spending values, while a smaller set has much higher spending."
            )
        with right:
            st.markdown("#### Spending snapshot")
            st.metric("Mean spending", f"${model_df['TOTEXP23'].mean():,.0f}")
            st.metric("Median spending", f"${model_df['TOTEXP23'].median():,.0f}")
            st.metric("Highest row value", f"${model_df['TOTEXP23'].max():,.0f}")
            callout(
                "Reading spending outcomes",
                "Large expenditure values can strongly affect regression metrics. Median and high-cost segment checks help keep the review grounded.",
            )

with tab_segments:
    segment_files = {
        "Objective 1 high-cost segment review": "objective1_segment",
        "Objective 3 high-cost segment review": "objective3_segment",
    }
    for label, key in segment_files.items():
        st.subheader(label)
        df = _load(key)
        if df is None or df.empty:
            st.warning(missing_data_note(f"data/processed/{MEPS_FILES[key]}"))
            continue
        if "segment" not in df.columns:
            st.warning(f"`{MEPS_FILES[key]}` is present, but it does not include a `segment` column.")
            st.dataframe({"Column": list(df.columns)}, use_container_width=True, hide_index=True)
            continue
        st.plotly_chart(high_cost_segment_chart(df, label), use_container_width=True)
        chart_caption(
            "Each segment represents an upper slice of the spending distribution. Error metrics describe model behavior within those high-cost groups."
        )
        if "threshold" in df.columns:
            st.dataframe(
                display_columns(df),
                use_container_width=True,
                hide_index=True,
                column_config={"threshold": st.column_config.NumberColumn("Threshold", format="$%.0f")},
            )
        else:
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

with tab_quintiles:
    df = _load("quintile")
    if df is None or df.empty:
        st.warning(missing_data_note(f"data/processed/{MEPS_FILES['quintile']}"))
    else:
        st.plotly_chart(quintile_heatmap(df), use_container_width=True)
        chart_caption(
            "Cells show how often rows fall into each actual and predicted spending group. A stronger ranking pattern appears closer to the diagonal."
        )
        callout(
            "Predicted and actual groups",
            "This table is a model review artifact. It helps inspect spending-group ranking behavior, not individual financial hardship.",
        )
        with st.expander("Saved quintile table"):
            st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

with tab_skew:
    df = _load("skew")
    if df is None or df.empty:
        st.warning(missing_data_note(f"data/processed/{MEPS_FILES['skew']}"))
    else:
        metric_cols = [
            col
            for col in ["dollar_MAE", "dollar_RMSE", "high_cost_MAE", "capture_rate_top20pct", "log_MAE", "log_RMSE", "dollar_R2"]
            if col in df.columns
        ]
        selected_metric = st.selectbox("Skew-aware metric", metric_cols, index=0, format_func=friendly_label) if metric_cols else None
        if selected_metric:
            lower_is_better = selected_metric not in {"capture_rate_top20pct", "dollar_R2"}
            st.plotly_chart(regression_metric_chart(df, selected_metric, lower_is_better=lower_is_better), use_container_width=True)
            chart_caption(
                "Skew-aware outputs compare models under log-scale and dollar-scale views. Lower error is better for MAE and RMSE; higher is better for capture rate and R-squared."
            )
        else:
            st.info("No standard skew-aware metric columns were found for charting.")
        callout(
            "Skewed expenditure outcomes",
            "A small number of high-cost cases can strongly affect dollar-scale error. Robust and log-scale checks help show whether patterns hold under another view of spending.",
        )
        st.dataframe(display_columns(df), use_container_width=True, hide_index=True)

with tab_files:
    file_rows = []
    for label, filename in MEPS_FILES.items():
        df = load_csv(filename)
        file_rows.append(
            {
                "File": filename,
                "Status": "Available" if df is not None and not df.empty else "Missing or empty",
                "Rows": len(df) if df is not None and not df.empty else None,
                "Columns": len(df.columns) if df is not None and not df.empty else None,
            }
        )
    st.dataframe(pd.DataFrame(file_rows), use_container_width=True, hide_index=True)

    preview_options = [row["File"] for row in file_rows if row["Status"] == "Available"]
    if preview_options:
        selected_file = st.selectbox("Preview an available MEPS file", preview_options)
        preview_df = load_csv(selected_file)
        if preview_df is not None:
            st.dataframe(display_columns(preview_df.head(50)), use_container_width=True, hide_index=True)
