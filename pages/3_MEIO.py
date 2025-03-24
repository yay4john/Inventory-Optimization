import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

st.set_page_config(page_title="Multi-Echelon Demo")

st.markdown("# Network Balancing and Multi-Echelon Inventory Optimization")
st.sidebar.header("Multi-Echelon Demo")
st.write(
    """
    Develop a simplified model or scenario analysis to determine optimal inventory allocation across a network, and create a multi-echelon model that calculates optimal inventory levels across different tiers, demonstrating how risk and variability propagate through a supply chain.
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

# Function to calculate inventory cost
def calculate_inventory_cost(safety_stock, holding_cost_per_unit, order_cost, demand_mean, order_quantity):
    holding_cost = safety_stock * holding_cost_per_unit
    ordering_cost = (demand_mean / order_quantity) * order_cost
    return holding_cost + ordering_cost

# Function to calculate multi-echelon safety stock
def calculate_multi_echelon_safety_stock(demand_std, lead_time, lead_time_std, service_level, num_echelons):
    base_safety_stock = calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level)
    echelon_factor = np.sqrt(num_echelons)  # Assumes risk pooling effect
    return base_safety_stock / echelon_factor

# Streamlit UI Setup
st.title("Inventory Optimization Tool")
st.sidebar.header("Input Parameters")

# User Inputs
demand_mean = st.sidebar.number_input("Average Demand per Period", min_value=1, value=100)
demand_std = st.sidebar.number_input("Demand Standard Deviation", min_value=0, value=20)
lead_time = st.sidebar.number_input("Lead Time (days)", min_value=1, value=5)
lead_time_std = st.sidebar.number_input("Lead Time Standard Deviation", min_value=0, value=2)
service_level = st.sidebar.number_input("Service Level (%)", min_value=50.0, max_value=99.99, value=95.0)
holding_cost_per_unit = st.sidebar.number_input("Holding Cost per Unit ($)", min_value=0.01, value=1.0)
order_cost = st.sidebar.number_input("Ordering Cost ($)", min_value=1.0, value=50.0)
order_quantity = st.sidebar.number_input("Order Quantity", min_value=1, value=500)
num_echelons = st.sidebar.number_input("Number of Echelons", min_value=1, value=2)

# Compute Safety Stock and Reorder Point
safety_stock = calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level)
reorder_point = calculate_reorder_point(demand_mean, lead_time, safety_stock)
inventory_cost = calculate_inventory_cost(safety_stock, holding_cost_per_unit, order_cost, demand_mean, order_quantity)
multi_echelon_safety_stock = calculate_multi_echelon_safety_stock(demand_std, lead_time, lead_time_std, service_level, num_echelons)

st.write(f"### Recommended Safety Stock: {round(safety_stock)} units")
st.write(f"### Multi-Echelon Safety Stock: {round(multi_echelon_safety_stock)} units")
st.write(f"### Reorder Point: {round(reorder_point)} units")
st.write(f"### Estimated Annual Inventory Cost: ${round(inventory_cost, 2)}")

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

# Inventory Bar Chart - Full Bottom Row
ax_big = fig.add_subplot(2, 1, 2)
ax_big.bar(["Inventory"], [order_quantity], color='lightblue', label="Cycle Stock")
ax_big.bar(["Inventory"], [safety_stock], bottom=[order_quantity], color='green', label="Safety Stock")
ax_big.axhline(reorder_point, color='r', linestyle='--', label="Reorder Point")
ax_big.set_title("Average Inventory Composition")
ax_big.legend()

fig.delaxes(axes[1, 1])  # Remove the empty subplot
fig.delaxes(axes[1, 0])  
plt.tight_layout()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on safety stock, reorder point, multi-echelon inventory optimization, and cost calculations.")
