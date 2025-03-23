import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Centralization vs. Decentralization")

st.markdown("# Network Design and Inventory Allocation")
st.sidebar.header("Centralization Demo")
st.write(
    """
    Compare the safety stock requirements of independent systems versus a pooled system using sample data to illustrate the benefits of risk pooling.
"""
)