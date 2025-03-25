import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

st.set_page_config(page_title="Single Echelon Demo")

st.markdown("# SEIO Fundamentals")
st.sidebar.header("Single Echelon Demo")
st.write(
    """
    Develop a model to calculate safety stock. Research and apply appropriate methods to determine safety stock levels under varying conditions.
"""
)

# Function to calculate safety stock
def calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level):
    z = stats.norm.ppf(service_level / 100)  # Convert service level percentage to Z-score
    safety_stock = z * np.sqrt((demand_std ** 2 * lead_time) + (demand_std ** 2 * lead_time_std ** 2))
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
lead_time_std = st.sidebar.number_input("Lead Time Standard Deviation", min_value=0, value=2)
service_level = st.sidebar.number_input("Service Level (%)", min_value=50.0, max_value=99.99, value=95.0)
order_quantity = st.sidebar.number_input("Order Quantity", min_value=1, value=750)
simulation_days = st.sidebar.number_input("Simulation Days", min_value=10, max_value=365, value=40)

# Compute Safety Stock and Reorder Point
safety_stock = calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level)
reorder_point = calculate_reorder_point(demand_mean, lead_time, safety_stock)

st.write(f"### Recommended Safety Stock: {round(safety_stock)} units")
st.write(f"### Reorder Point: {round(reorder_point)} units")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 8), gridspec_kw={'height_ratios': [1, 1.5]})

# Demand Distribution Plot
x = np.linspace(demand_mean - 3*demand_std, demand_mean + 3*demand_std, 100)
y = (1 / (demand_std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - demand_mean) / demand_std) ** 2)
axes[0, 0].plot(x, y, label="Demand Distribution")
axes[0, 0].axvline(demand_mean, color='r', linestyle='--', label="Mean Demand")
axes[0, 0].set_title("Demand Distribution")
axes[0, 0].legend()

# Lead Time Distribution Plot
lead_time_x = np.linspace(lead_time - 3*lead_time_std, lead_time + 3*lead_time_std, 100)
lead_time_y = (1 / (lead_time_std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((lead_time_x - lead_time) / lead_time_std) ** 2)
axes[0, 1].plot(lead_time_x, lead_time_y, label="Lead Time Distribution", color='orange')
axes[0, 1].axvline(lead_time, color='r', linestyle='--', label="Mean Lead Time")
axes[0, 1].set_title("Lead Time Distribution")
axes[0, 1].legend()

# Inventory Line Plot Simulation
inventory_levels = []
current_inventory = order_quantity
for day in range(simulation_days):
    daily_demand = np.random.normal(demand_mean, demand_std)
    current_inventory -= daily_demand
    if current_inventory <= reorder_point:
        current_inventory += order_quantity
    inventory_levels.append(current_inventory)

# Inventory Bar Chart - Full Bottom Row
ax_big = fig.add_subplot(2, 1, 2)
ax_big.plot(range(simulation_days), inventory_levels, label="Inventory Level", color='blue')
ax_big.axhline(safety_stock, color='green', linestyle='--', label="Safety Stock")
ax_big.axhline(reorder_point, color='red', linestyle='--', label="Reorder Point")
ax_big.set_title("Inventory Over Time")
ax_big.legend()

fig.delaxes(axes[1, 1])  # Remove the empty subplot
fig.delaxes(axes[1, 0])  
plt.tight_layout()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on safety stock and reorder point.")