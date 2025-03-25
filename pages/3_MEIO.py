import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd

# Function to calculate safety stock incorporating lead time variability
def calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level):
    z = stats.norm.ppf(service_level / 100)  # Convert service level percentage to Z-score
    safety_stock = z * np.sqrt((demand_std ** 2 * lead_time) + (demand_std ** 2 * lead_time_std ** 2))
    return int(safety_stock)

# Function to calculate reorder point
def calculate_reorder_point(demand_mean, lead_time, safety_stock):
    return int((demand_mean * lead_time) + safety_stock)

# Streamlit UI Setup
st.title("Inventory Optimization Tool")
st.sidebar.header("Input Parameters")

# User Inputs
order_quantity = st.sidebar.number_input("Order Quantity", min_value=1, value=750)
simulation_days = st.sidebar.number_input("Simulation Days", min_value=10, max_value=365, value=40)

# Compute Safety Stock and Reorder Point
safety_stock = calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level)
reorder_point = calculate_reorder_point(demand_mean, lead_time, safety_stock)

# Inventory Line Plot Simulation with Lead Time
inventory_levels = []
current_inventory = order_quantity
order_pending = False
order_count = 0
lead_time_remaining = 0
stock_out = 0
for day in range(simulation_days):
    daily_demand = int(np.random.normal(demand_mean, demand_std))
    current_inventory -= daily_demand
    
    if order_pending:
        lead_time_remaining -= 1
        if lead_time_remaining <= 0:
            current_inventory += order_quantity
            order_pending = False
    
    if current_inventory <= reorder_point and not order_pending:
        order_pending = True
        order_count += 1
        lead_time_remaining = max(1, int(np.random.normal(lead_time, lead_time_std)))
    
    if current_inventory < 0:
        stock_out -= current_inventory

    inventory_levels.append(current_inventory)

# calculate average inventory level
average_inventory = sum(inventory_levels) / len(inventory_levels)

# Function to calculate inventory cost
def calculate_inventory_cost(holding_cost_per_unit, order_cost):
    holding_cost = average_inventory * holding_cost_per_unit
    ordering_cost = order_count * order_cost
    return holding_cost + ordering_cost

inventory_cost = calculate_inventory_cost(holding_cost_per_unit, order_cost)
stock_out_cost = stock_out * stock_out_cost_per_unit

# Echelon 1 Table
echelon1_df = pd.DataFrame(columns=['Warehouse', 'Holding $/Unit'])
st.write("### Echelon 1: Warehouses")
st.dataframe(echelon1_df)

# Echelon 2 Table
echelon2_df = pd.DataFrame(columns=['Customer', 'Avg. Demand', 'St. Dev. Demand', 'Holding $/Unit', 'Stock Out $/Unit', 'Service Level'])
st.write("### Echelon 2: Customers")
st.dataframe(echelon2_df)

# Network Table
network_df = pd.DataFrame(columns=['Warehouse', 'Customer', 'Order Cost', 'Avg. Lead Time', 'St. Dev. Lead Time'])
st.write("### Network Configuration")
st.dataframe(network_df)

st.write(f"### Estimated Annual Inventory Cost: ${round(inventory_cost, 2)}")
st.write(f"### Estimated Stock-Out Cost: ${round(stock_out_cost, 2)}")

# Visualization
fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# Inventory Line Plot Simulation with Lead Time
inventory_levels = []
current_inventory = order_quantity
order_pending = False
lead_time_remaining = 0
for day in range(simulation_days):
    daily_demand = np.random.normal(demand_mean, demand_std)
    current_inventory -= daily_demand
    
    if order_pending:
        lead_time_remaining -= 1
        if lead_time_remaining <= 0:
            current_inventory += order_quantity
            order_pending = False
    
    if current_inventory <= reorder_point and not order_pending:
        order_pending = True
        lead_time_remaining = max(1, int(np.random.normal(lead_time, lead_time_std)))
    
    inventory_levels.append(current_inventory)

axes[0].plot(range(simulation_days), inventory_levels, label="Inventory Level", color='blue')
axes[0].axhline(safety_stock, color='green', linestyle='--', label="Safety Stock")
axes[0].axhline(reorder_point, color='red', linestyle='--', label="Reorder Point")
axes[0].set_title("Inventory Over Time")
axes[0].legend()

# Cost Comparison Bar Chart
axes[1].barh(["Holding Cost", "Stock-Out Cost"], [inventory_cost, stock_out_cost], color=['blue', 'red'])
axes[1].set_title("Cost Comparison")
axes[1].set_xlabel("Cost ($)")

plt.tight_layout()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on inventory levels, safety stock, reorder point, and costs.")