import streamlit as st

from utils.data_loader import list_processed_files, load_csv
from utils.metrics import format_count, format_percent
from utils.text_blocks import apply_page_style, home_intro, metric_card, missing_data_note


st.set_page_config(
    page_title="Healthcare Access & Cost Burden Explorer",
    page_icon="⚕️",
    layout="wide",
)

apply_page_style()

st.title("Healthcare Access & Cost Burden Explorer")
st.caption("A readable workspace for processed public-use survey outputs and saved model artifacts.")

st.markdown(home_intro())

processed_files = list_processed_files()
nhis_files = [name for name in processed_files if name.lower().startswith("nhis_")]
meps_files = [name for name in processed_files if name.lower().startswith("meps_")]

model_ready = load_csv("nhis_model_ready_v1.csv")
outcome_text = "File missing"
model_rows_text = "File missing"
if model_ready is not None and not model_ready.empty:
    model_rows_text = format_count(len(model_ready))
    if "mental_health_cost_barrier" in model_ready.columns:
        outcome_text = format_percent(model_ready["mental_health_cost_barrier"].mean())

model_artifact_count = len(
    [
        name
        for name in processed_files
        if "model" in name.lower() or "threshold" in name.lower() or "feature_importance" in name.lower()
    ]
)

card_a, card_b, card_c, card_d = st.columns(4)
with card_a:
    st.markdown(
        metric_card(
            "NHIS outputs",
            format_count(len(nhis_files)) if nhis_files else "None found",
            "Processed NHIS CSV files available for the explorer and model pages.",
        ),
        unsafe_allow_html=True,
    )
with card_b:
    st.markdown(
        metric_card(
            "Model-ready rows",
            model_rows_text,
            "Rows in the saved NHIS modeling file used for snapshots and checks.",
        ),
        unsafe_allow_html=True,
    )
with card_c:
    st.markdown(
        metric_card(
            "Measured barrier",
            outcome_text,
            "Share of model-ready NHIS rows marked with a mental health cost barrier.",
        ),
        unsafe_allow_html=True,
    )
with card_d:
    st.markdown(
        metric_card(
            "Model artifacts",
            "NHIS + MEPS",
            "Saved comparison, feature-importance, threshold-review, high-cost segment, predicted-vs-actual, and skew-aware review files used to explain model behavior in the app.",
        ),
        unsafe_allow_html=True,
    )

st.divider()

st.subheader("Start with a question")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        """
        **NHIS Explorer**

        Compare survey-weighted rates across income, region, sex, disability status,
        functioning difficulties, mental health history, and affordability pressures.
        """
    )
    st.markdown(
        """
        **Model Lab**

        Review saved model comparisons, feature importance, and threshold tradeoffs
        without retraining or scoring new records.
        """
    )

with col_b:
    st.markdown(
        """
        **Ethics and Limitations**

        Keep the interpretation grounded: public-use data, survey weights, model limits,
        and no individual decision-making.
        """
    )
    st.markdown(
        """
        **Data Dictionary**

        Use the reference table when you need to connect plain-language labels back to
        variable names and saved output files.
        """
    )

if not processed_files:
    st.warning(missing_data_note("data/processed"))

with st.expander("Available processed files"):
    if processed_files:
        st.dataframe({"file": processed_files}, use_container_width=True, hide_index=True)
    else:
        st.write("No processed CSV files were found.")

if meps_files:
    st.info(f"{format_count(len(meps_files))} processed MEPS file(s) were found. Open the MEPS page for a quick file preview.")
else:
    st.info("No app-ready MEPS CSV files were found in processed outputs yet, so the MEPS page stays in reference mode.")
