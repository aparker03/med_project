import streamlit as st

from utils.charts import distribution_chart
from utils.data_loader import list_csv_files, load_csv_from_path
from utils.labels import display_columns, friendly_label
from utils.metrics import format_count
from utils.text_blocks import apply_page_style, chart_caption


st.set_page_config(page_title="MEPS Explorer", layout="wide")
apply_page_style()

st.title("MEPS Explorer")
st.caption("A light preview page for processed or interim MEPS CSV outputs when they are available.")

meps_files = [
    path
    for path in list_csv_files(["data/processed", "data/interim"])
    if path.name.lower().startswith("meps_") or "meps" in path.name.lower()
]

if not meps_files:
    st.info(
        "No app-ready MEPS CSV files were found in `data/processed` or `data/interim`. "
        "This page intentionally avoids raw files and will become active once a processed or interim MEPS CSV is saved."
    )
    st.stop()

file_options = {str(path.relative_to(path.parents[2])): path for path in meps_files}
selected = st.selectbox("MEPS file", list(file_options.keys()))
df = load_csv_from_path(file_options[selected])

if df is None or df.empty:
    st.warning(f"`{selected}` could not be loaded or is empty.")
    st.stop()

col_a, col_b, col_c = st.columns(3)
col_a.metric("Rows", format_count(len(df)))
col_b.metric("Columns", format_count(len(df.columns)))
col_c.metric("Missing values", format_count(int(df.isna().sum().sum())))

numeric_cols = list(df.select_dtypes(include="number").columns)
if numeric_cols:
    selected_col = st.selectbox("Choose a numeric field", numeric_cols, format_func=friendly_label)
    st.plotly_chart(distribution_chart(df, selected_col), use_container_width=True)
    chart_caption("This preview shows the shape of the saved MEPS file. It does not apply survey design methods or model training.")
else:
    st.info("This MEPS file does not contain numeric columns for a quick distribution chart.")

with st.expander("Preview rows"):
    st.dataframe(display_columns(df.head(100)), use_container_width=True, hide_index=True)
