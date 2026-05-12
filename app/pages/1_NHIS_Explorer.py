import streamlit as st

from utils.charts import bar_rate_chart, distribution_chart
from utils.data_loader import list_weighted_rate_files, load_csv
from utils.labels import (
    dataset_label,
    display_columns,
    friendly_label,
    group_key_from_filename,
    interpretation_for_group,
    label_group_values,
    sort_weighted_rate_rows,
)
from utils.metrics import format_count, format_percent
from utils.text_blocks import apply_page_style, callout, caution_note, chart_caption, missing_data_note, small_note


st.set_page_config(page_title="NHIS Explorer", page_icon="⚕️", layout="wide")
apply_page_style()

st.title("NHIS Explorer")
st.caption("A guided view of saved NHIS weighted-rate outputs.")

weighted_files = list_weighted_rate_files()

if not weighted_files:
    st.warning(missing_data_note("data/processed/nhis_weighted_rate_by_*.csv"))
    st.stop()

st.markdown(
    "Choose a grouping below to compare the survey-weighted rate of the measured mental health cost barrier. "
    "These are descriptive estimates from saved CSV files, not a causal analysis."
)

tab_rates, tab_model_ready = st.tabs(["Weighted rates", "Model-ready snapshot"])

with tab_rates:
    file_options = {dataset_label(name): name for name in weighted_files}
    selected_label = st.selectbox("Choose a grouping", list(file_options.keys()))
    selected_file = file_options[selected_label]
    selected_variable = group_key_from_filename(selected_file)
    small_note(f"Source variable: `{selected_variable}`")
    rate_df = load_csv(selected_file)

    if rate_df is None or rate_df.empty:
        st.warning(missing_data_note(f"data/processed/{selected_file}"))
        st.stop()

    rate_df = label_group_values(rate_df, selected_file)

    required_cols = {"group_display", "weighted_rate", "unweighted_n"}
    if not required_cols.issubset(rate_df.columns):
        st.error(
            "This rate file is present, but it does not have the columns the explorer expects. "
            "Expected: `group`, `unweighted_n`, and `weighted_rate`."
        )
        st.write("Available columns:")
        st.dataframe({"Column": list(rate_df.columns)}, use_container_width=True, hide_index=True)
        with st.expander("Preview the first rows"):
            st.dataframe(rate_df.head(50), use_container_width=True)
        st.stop()

    rate_df = sort_weighted_rate_rows(rate_df, selected_file)
    top_row = rate_df.sort_values("weighted_rate", ascending=False).iloc[0]
    low_row = rate_df.sort_values("weighted_rate", ascending=True).iloc[0]

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Groups", format_count(rate_df["group_display"].nunique()))
    col_b.metric("Highest rate", format_percent(top_row["weighted_rate"]), top_row["group_display"])
    col_c.metric("Lowest rate", format_percent(low_row["weighted_rate"]), low_row["group_display"])

    callout("Reading this view", interpretation_for_group(selected_file))
    caution_note(
        "Caution: weighted survey rates help describe group patterns. They do not prove cause and effect, and small raw sample counts can make estimates less stable."
    )

    st.plotly_chart(bar_rate_chart(rate_df, f"Mental health cost-barrier rate by {selected_label}"), use_container_width=True)
    chart_caption(
        "Bars show the survey-weighted rate for each group. The yellow markers show the raw sample rate when that column is available. Hover over a bar to see the raw sample count."
    )

    display_cols = [
        "group_display",
        "unweighted_n",
        "weighted_rate",
        "unweighted_rate",
    ]
    display_cols = [col for col in display_cols if col in rate_df.columns]
    table_df = rate_df[display_cols].sort_values("weighted_rate", ascending=False).rename(
        columns={
            "group_display": "Group",
            "unweighted_n": "Raw sample count",
            "weighted_rate": "Survey-weighted rate",
            "unweighted_rate": "Raw sample rate",
        }
    )
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Raw sample count": st.column_config.NumberColumn("Raw sample count", format="%d"),
            "Survey-weighted rate": st.column_config.ProgressColumn("Survey-weighted rate", format="%.1%%", min_value=0, max_value=1),
            "Raw sample rate": st.column_config.ProgressColumn("Raw sample rate", format="%.1%%", min_value=0, max_value=1),
        },
    )
    chart_caption("The raw sample count is not weighted; it helps show how many survey records sit behind each group estimate.")

with tab_model_ready:
    model_df = load_csv("nhis_model_ready_v1.csv")

    if model_df is None or model_df.empty:
        st.warning(missing_data_note("data/processed/nhis_model_ready_v1.csv"))
    else:
        st.subheader("Saved modeling file")
        metric_cols = st.columns(4)
        metric_cols[0].metric("Rows", format_count(len(model_df)))
        metric_cols[1].metric("Columns", format_count(len(model_df.columns)))
        if "mental_health_cost_barrier" in model_df.columns:
            metric_cols[2].metric("Barrier rate", format_percent(model_df["mental_health_cost_barrier"].mean()))
        else:
            metric_cols[2].metric("Barrier rate", "Column missing")
        metric_cols[3].metric("Missing values", format_count(int(model_df.isna().sum().sum())))

        st.markdown("#### Quick distributions")
        distribution_candidates = [
            "affordability_pressure_count",
            "mental_health_history_count",
            "functioning_difficulty_count",
            "chronic_condition_count",
            "SEX_A",
            "REGION",
            "DISAB3_A",
            "poverty_group_imp",
        ]
        available = [col for col in distribution_candidates if col in model_df.columns]
        if available:
            selected_col = st.selectbox("Choose a field", available, format_func=friendly_label)
            st.plotly_chart(distribution_chart(model_df, selected_col), use_container_width=True)
            chart_caption(
                "This chart is a row-level snapshot from the saved model-ready file. It is useful for orientation, not a substitute for survey-weighted estimates."
            )
        else:
            st.info("No standard app variables were found for distribution charts.")

        with st.expander("Preview model-ready rows"):
            preview_cols = [
                col
                for col in [
                    "mental_health_cost_barrier",
                    "AGEP_A",
                    "SEX_A",
                    "REGION",
                    "POVRATTC_A",
                    "affordability_pressure_count",
                    "mental_health_history_count",
                    "functioning_difficulty_count",
                ]
                if col in model_df.columns
            ]
            st.dataframe(display_columns(model_df[preview_cols].head(100)), use_container_width=True, hide_index=True)
