"""
1_Upload.py
=============
Streamlit page skeleton: dataset / telemetry upload.

Placeholder UI only — not wired to `src/pipeline/feature_fusion.py` yet.
"""

import streamlit as st

st.title("Upload")
st.caption("Select a dataset or upload raw telemetry to run through the pipeline.")

dataset = st.selectbox("Dataset", ["CIC-IDS-2018", "CTU-13", "Upload custom..."])

if dataset == "Upload custom...":
    st.file_uploader("Upload raw telemetry (CSV/PCAP)", type=["csv", "pcap"])

st.button("Run Feature Pipeline", disabled=True, help="Not yet wired to src/pipeline/feature_fusion.py")

st.info("This page is a UI skeleton. Wiring to the real pipeline is a WS1 task.")
