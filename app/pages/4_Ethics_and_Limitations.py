import streamlit as st

from utils.text_blocks import apply_page_style, ethics_sections


st.set_page_config(page_title="Ethics and Limitations", layout="wide")
apply_page_style()

st.title("Ethics and Limitations")
st.caption("How to read the app responsibly.")

for title, body in ethics_sections():
    st.subheader(title)
    st.markdown(body)
