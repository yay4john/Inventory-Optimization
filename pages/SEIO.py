import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Single Echelon Demo")

# Function to calculate safety stock
def calculate_safety_stock(demand_mean, demand_std, lead_time, service_level):
    z_scores = {90: 1.28, 95: 1.65, 99: 2.33}
    z = z_scores.get(service_level, 1.65)  # Default to 95%
    safety_stock = z * demand_std * np.sqrt(lead_time)
    return safety_stock

# Function to calculate reorder point
def calculate_reorder_point(demand_mean, lead_time, safety_stock):
    return (demand_mean * lead_time) + safety_stock

# Streamlit UI Setup
st.title("Inventory Optimization Tool")
st.sidebar.header("Input Parameters")

# User Inputs
demand_mean = st.sidebar.number_input("Average Demand per Period", min_value=1, value=100)
demand_std = st.sidebar.number_input("Demand Standard Deviation", min_value=0, value=20)
lead_time = st.sidebar.number_input("Lead Time (days)", min_value=1, value=5)
service_level = st.sidebar.selectbox("Service Level (%)", [90, 95, 99], index=1)

# Compute Safety Stock and Reorder Point
safety_stock = calculate_safety_stock(demand_mean, demand_std, lead_time, service_level)
reorder_point = calculate_reorder_point(demand_mean, lead_time, safety_stock)

st.write(f"### Recommended Safety Stock: {round(safety_stock)} units")
st.write(f"### Reorder Point: {round(reorder_point)} units")

# Visualization
fig, ax = plt.subplots()
x = np.linspace(demand_mean - 3*demand_std, demand_mean + 3*demand_std, 100)
y = (1 / (demand_std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - demand_mean) / demand_std) ** 2)
ax.plot(x, y, label="Demand Distribution")
ax.axvline(demand_mean, color='r', linestyle='--', label="Mean Demand")
ax.axvline(demand_mean + safety_stock, color='g', linestyle='--', label="Safety Stock Level")
ax.axvline(reorder_point, color='b', linestyle='--', label="Reorder Point")
ax.legend()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on safety stock and reorder point.")
