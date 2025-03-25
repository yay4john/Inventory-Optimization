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
    return int(safety_stock)

# Function to calculate reorder point
def calculate_reorder_point(demand_mean, lead_time, safety_stock):
    return int((demand_mean * lead_time) + safety_stock)

# Streamlit UI Setup
st.title("Inventory Optimization Tool")
st.sidebar.header("Input Parameters")

# User Inputs
demand_mean = st.sidebar.number_input("Average Demand per Day", min_value=1, value=5)
demand_std = st.sidebar.number_input("Demand Standard Deviation", min_value=0, value=1)
lead_time = st.sidebar.number_input("Lead Time (days)", min_value=0, value=2)
lead_time_std = st.sidebar.number_input("Lead Time Standard Deviation", min_value=0, value=1)
service_level = st.sidebar.number_input("Service Level (%)", min_value=0.01, max_value=99.99, value=95.0)
holding_cost_per_unit = st.sidebar.number_input("Holding Cost per Unit ($)", min_value=0.01, value=50.0)
order_cost = st.sidebar.number_input("Ordering Cost ($)", min_value=0.01, value=3.0)
order_quantity = st.sidebar.number_input("Order Quantity", min_value=1, value=20)
stock_out_cost_per_unit = st.sidebar.number_input("Stock-Out Cost per Unit ($)", min_value=0.01, value=25.0)
simulation_days = st.sidebar.number_input("Simulation Days", min_value=1, max_value=365, value=20)

# Compute Safety Stock and Reorder Point
safety_stock = calculate_safety_stock(demand_std, lead_time, lead_time_std, service_level)
reorder_point = calculate_reorder_point(demand_mean, lead_time, safety_stock)

# EOQ Tradeoff Chart
eoq = np.sqrt((2 * demand_mean * 365 * order_cost) / holding_cost_per_unit)
quantity = np.linspace(1, eoq*1.5, 100)
holding_cost = (holding_cost_per_unit * quantity)/2
ordering_cost = (order_cost*demand_mean*365) / quantity
total_cost = holding_cost + ordering_cost

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

st.write(f"### Recommended Safety Stock: {round(safety_stock)} units")
st.write(f"### Reorder Point: {round(reorder_point)} units")
st.write(f"### Estimated Annual Inventory Cost: ${round(inventory_cost, 2)}")
st.write(f"### Estimated Stock-Out Cost: ${round(stock_out_cost, 2)}")
st.write(f"### Economic Order Quantity: {round(eoq, 0)}")

# Visualization
fig, axes = plt.subplots(3, 1, figsize=(8, 15))

axes[0].plot(range(simulation_days), inventory_levels, label="Inventory Level", color='blue')
axes[0].axhline(safety_stock, color='green', linestyle='--', label="Safety Stock")
axes[0].axhline(reorder_point, color='red', linestyle='--', label="Reorder Point")
axes[0].axhline(average_inventory, color='black', linestyle='--', label="Avg. Inventory")
axes[0].set_title("Inventory Over Time")
axes[0].legend()

# Cost Comparison Bar Chart
axes[1].barh(["Holding Cost", "Stock-Out Cost"], [inventory_cost, stock_out_cost], color=['blue', 'red'])
axes[1].set_title("Cost Comparison")
axes[1].set_xlabel("Cost ($)")



axes[2].plot(quantity, holding_cost, label="Holding Cost", color='blue')
axes[2].plot(quantity, ordering_cost, label="Ordering Cost", color='red')
axes[2].plot(quantity, total_cost, label="Total Cost", color='black', linestyle='dashed')
axes[2].axvline(eoq, color='cyan', linestyle='--', label="EOQ")
axes[2].set_title("EOQ Tradeoff Chart")
axes[2].legend()


plt.tight_layout()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on safety stock, reorder point, and cost calculations.")
