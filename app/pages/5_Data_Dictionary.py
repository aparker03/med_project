import pandas as pd
import streamlit as st

from utils.data_loader import load_csv
from utils.labels import dictionary_rows, friendly_label
from utils.text_blocks import apply_page_style


st.set_page_config(page_title="Data Dictionary", layout="wide")
apply_page_style()

st.title("Data Dictionary")
st.caption("A companion reference for tracing plain-language labels back to variables and saved output files.")

st.markdown(
    """
The main pages use readable labels first. This page keeps the technical names nearby for
review, codebook checks, and handoff to analysis notebooks.
"""
)

nhis_model_df = load_csv("nhis_model_ready_v1.csv")
meps_model_df = load_csv("meps_model_ready_v1.csv")

available_columns = []
if nhis_model_df is not None and not nhis_model_df.empty:
    available_columns.extend(list(nhis_model_df.columns))
if meps_model_df is not None and not meps_model_df.empty:
    available_columns.extend([col for col in meps_model_df.columns if col not in available_columns])
dictionary_df = pd.DataFrame(dictionary_rows(available_columns))

search = st.text_input("Search labels, variable names, sources, or notes", "")
if search:
    mask = dictionary_df.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False))
    dictionary_df = dictionary_df[mask.any(axis=1)]

source_options = ["All sources"] + sorted(dictionary_df["Source file or output file"].dropna().unique())
selected_source = st.selectbox("Filter by source", source_options)
if selected_source != "All sources":
    dictionary_df = dictionary_df[dictionary_df["Source file or output file"] == selected_source]

st.dataframe(dictionary_df, use_container_width=True, hide_index=True)

if nhis_model_df is not None and not nhis_model_df.empty:
    st.subheader("NHIS model-ready columns")
    columns_df = pd.DataFrame(
        {
            "Plain-language label": [friendly_label(col) for col in nhis_model_df.columns],
            "Variable name": list(nhis_model_df.columns),
            "Type": [str(dtype) for dtype in nhis_model_df.dtypes],
        }
    )
    st.dataframe(columns_df, use_container_width=True, hide_index=True)
else:
    st.info("The NHIS model-ready file was not found, so only the curated dictionary is shown.")

if meps_model_df is not None and not meps_model_df.empty:
    st.subheader("MEPS model-ready columns")
    columns_df = pd.DataFrame(
        {
            "Plain-language label": [friendly_label(col) for col in meps_model_df.columns],
            "Variable name": list(meps_model_df.columns),
            "Type": [str(dtype) for dtype in meps_model_df.dtypes],
        }
    )
    st.dataframe(columns_df, use_container_width=True, hide_index=True)
else:
    st.info("The MEPS model-ready file was not found, so MEPS concept entries are shown without a full model-ready column listing.")
