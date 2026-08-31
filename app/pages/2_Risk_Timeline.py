"""
2_Risk_Timeline.py
=====================
Streamlit page skeleton: live risk score / MITRE stage timeline.

Placeholder UI only — not wired to `src/heads/prediction_heads.py` yet.
"""

import streamlit as st

st.title("Risk Timeline")
st.caption("Risk score and predicted MITRE ATT&CK stage over time.")

st.selectbox("Entity", ["(no data loaded)"], disabled=True)

st.info(
    "This page is a UI skeleton. Once wired to "
    "src/heads/prediction_heads.py, it will render a time series of "
    "RiskScoreHead output alongside MitreStageClassifierHead predictions."
)
