import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd

# Function to calculate safety stock incorporating lead time variability
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
num_echelons = st.sidebar.number_input("Number of Echelons", min_value=1, value=2)
stock_out_cost_per_unit = st.sidebar.number_input("Stock-Out Cost per Unit ($)", min_value=0.01, value=5.0)
simulation_days = st.sidebar.number_input("Simulation Days", min_value=10, max_value=365, value=40)

# Echelon 1 Table
echelon1_df = pd.DataFrame(columns=['Warehouse', 'Holding $/Unit'])
st.write("### Echelon 1: Warehouses")
st.data_editor(echelon1_df, num_rows='dynamic')

# Echelon 2 Table
echelon2_df = pd.DataFrame(columns=['Customer', 'Avg. Demand', 'St. Dev. Demand', 'Holding $/Unit', 'Stock Out $/Unit', 'Service Level'])
st.write("### Echelon 2: Customers")
st.data_editor(echelon2_df, num_rows='dynamic')

# Network Table
network_df = pd.DataFrame(columns=['Warehouse', 'Customer', 'Order Cost', 'Avg. Lead Time', 'St. Dev. Lead Time'])
st.write("### Network Configuration")
st.data_editor(network_df, num_rows='dynamic')

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
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

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

# EOQ Tradeoff Chart
quantity = np.linspace(1, 2000, 100)
holding_cost = (holding_cost_per_unit * quantity) / 2
ordering_cost = (order_cost * demand_mean) / quantity
total_cost = holding_cost + ordering_cost
eoq = np.sqrt((2 * demand_mean * order_cost) / holding_cost_per_unit)

axes[2].plot(quantity, holding_cost, label="Holding Cost", color='blue')
axes[2].plot(quantity, ordering_cost, label="Ordering Cost", color='red')
axes[2].plot(quantity, total_cost, label="Total Cost", color='black', linestyle='dashed')
axes[2].axvline(eoq, color='cyan', linestyle='--', label="EOQ")
axes[2].set_title("EOQ Tradeoff Chart")
axes[2].legend()

plt.tight_layout()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on inventory levels, safety stock, reorder point, and costs.")
