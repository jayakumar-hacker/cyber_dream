"""
app.py
=======
Main entry point for the CyberDreamer Streamlit demo.

This is a UI skeleton only — it wires up page config and navigation.
The actual page content lives under `app/pages/`, and none of those
pages call into real model logic yet (see `src/` stub modules).

Run with:
    streamlit run app/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="CyberDreamer",
    page_icon=":shield:",
    layout="wide",
)

st.title("CyberDreamer")
st.caption("A Graph-RSSM World Model for Predictive Cyber Defense")

st.markdown(
    """
    Use the sidebar to navigate:

    - **Upload** — load raw telemetry / select a dataset (CIC-IDS-2018, CTU-13).
    - **Risk Timeline** — view the live risk score and MITRE stage over time.
    - **Rollout** — explore imagined future trajectories (K-step rollout).
    - **Explain** — inspect attention / SHAP attributions for a prediction.

    This is a scaffolded skeleton. Pages currently render placeholder UI
    only; they are not yet wired to a trained model.
    """
)
