import streamlit as st

st.set_page_config(page_title="Inventory Demo")

st.write("# Inventory Optimization Demo")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Working through the demos to the left, we aim to:

    Develop a model to calculate safety stock. Research and apply appropriate methods to determine safety stock levels under varying conditions.

    Build a toy cost model to quantify potential annual savings from optimizing inventory parameters, and discuss how these savings translate into strategic value.

    Develop a simplified model or scenario analysis to determine optimal inventory allocation across a network, and create a multi-echelon model that calculates optimal inventory levels across different tiers, demonstrating how risk and variability propagate through a supply chain.

    Compare the safety stock requirements of independent systems versus a pooled system using sample data to illustrate the benefits of risk pooling.

    Implement a simple simulation model that estimates demand variability and evaluates its impact on inventory decisions.
"""
)
