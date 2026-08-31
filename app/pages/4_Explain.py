"""
4_Explain.py
==============
Streamlit page skeleton: prediction explainability view.

Placeholder UI only — not wired to `src/explainability/` yet.
"""

import streamlit as st

st.title("Explain")
st.caption("Inspect attention and SHAP attributions behind a prediction.")

tab_attention, tab_shap = st.tabs(["Attention", "SHAP"])

with tab_attention:
    st.info(
        "This tab is a UI skeleton. Once wired to "
        "src/explainability/attention.py, it will show the top "
        "contributing nodes/edges for the selected prediction."
    )

with tab_shap:
    st.info(
        "This tab is a UI skeleton. Once wired to "
        "src/explainability/shap_wrapper.py, it will show per-feature "
        "SHAP attribution values."
    )
