"""
3_Rollout.py
==============
Streamlit page skeleton: imagined K-step rollout explorer.

Placeholder UI only — not wired to `src/simulator/rollout_engine.py` yet.
"""

import streamlit as st

st.title("Rollout")
st.caption("Explore imagined future trajectories from the current belief state.")

st.slider("K rollout steps", min_value=1, max_value=50, value=15, disabled=True)
st.slider("Number of trajectories", min_value=1, max_value=64, value=32, disabled=True)

st.info(
    "This page is a UI skeleton. Once wired to "
    "src/simulator/rollout_engine.py and "
    "src/explainability/trajectory_viz.py, it will render imagined "
    "latent trajectories projected into 2D/3D space."
)
