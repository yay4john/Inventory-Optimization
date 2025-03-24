import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

st.set_page_config(page_title="Single Echelon with Costs Demo")

st.markdown("# SEIO Solved with Financials")
st.sidebar.header("Single Echelon with Costs Demo")
st.write(
    """
    Build a toy cost model to quantify potential annual savings from optimizing inventory parameters, and discuss how these savings translate into strategic value.
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

# Function to calculate stock-out cost
def calculate_stock_out_cost(stock_out_cost_per_unit, safety_stock, demand_mean):
    expected_stockouts = max(0, demand_mean - safety_stock)
    return expected_stockouts * stock_out_cost_per_unit

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
order_quantity = st.sidebar.number_input("Order Quantity", min_value=1, value=750)
stock_out_cost_per_unit = st.sidebar.number_input("Stock-Out Cost per Unit ($)", min_value=0.01, value=5.0)

# Compute Safety Stock and Reorder Point
safety_stock = calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level)
reorder_point = calculate_reorder_point(demand_mean, lead_time, safety_stock)
inventory_cost = calculate_inventory_cost(safety_stock, holding_cost_per_unit, order_cost, demand_mean, order_quantity)
stock_out_cost = calculate_stock_out_cost(stock_out_cost_per_unit, safety_stock, demand_mean)

st.write(f"### Recommended Safety Stock: {round(safety_stock)} units")
st.write(f"### Reorder Point: {round(reorder_point)} units")
st.write(f"### Estimated Annual Inventory Cost: ${round(inventory_cost, 2)}")
st.write(f"### Estimated Stock-Out Cost: ${round(stock_out_cost, 2)}")

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

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

# Inventory Bar Chart
axes[1, 0].bar(["Inventory"], [order_quantity], color='lightblue', label="Cycle Stock")
axes[1, 0].bar(["Inventory"], [safety_stock], bottom=[order_quantity], color='green', label="Safety Stock")
axes[1, 0].axhline(reorder_point, color='r', linestyle='--', label="Reorder Point")
axes[1, 0].set_title("Average Inventory Composition")
axes[1, 0].set_xlim(-1, 1)
axes[1, 0].legend()

# Cost Comparison Bar Chart
axes[1, 1].barh(["Holding Cost", "Stock-Out Cost"], [inventory_cost, stock_out_cost], color=['blue', 'red'])
axes[1, 1].set_title("Cost Comparison")
axes[1, 1].set_xlabel("Cost ($)")

plt.tight_layout()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on safety stock, reorder point, and cost calculations.")
