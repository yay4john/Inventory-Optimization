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

# Function to calculate EOQ
def calculate_eoq(demand_mean, order_cost, holding_cost):
    return int(np.sqrt((2 * demand_mean * 365 * order_cost) / holding_cost))

# Streamlit UI Setup
st.title("Multi-Echelon Inventory Optimization Tool")
st.sidebar.header("Input Parameters")

simulation_days = st.sidebar.number_input("Simulation Days", min_value=1, max_value=365, value=20)

# Echelon 1 Table
echelon1_data = {'Warehouse': ['WH1'], 'Holding $/Unit': [1.50]}
echelon1_df = pd.DataFrame(echelon1_data)
st.write("### Echelon 1: Warehouses")
st.data_editor(echelon1_df, num_rows='dynamic')

# Echelon 2 Table
echelon2_data = {
    'Customer': ['C1', 'C2'],
    'Avg. Demand': [50, 40],
    'St. Dev. Demand': [10, 8],
    'Holding $/Unit': [2.00, 2.50],
    'Stock Out $/Unit': [5.00, 6.00],
    'Service Level': [95, 97]
}
echelon2_df = pd.DataFrame(echelon2_data)
st.write("### Echelon 2: Customers")
st.data_editor(echelon2_df, num_rows='dynamic')

# Network Table
network_data = {
    'Warehouse': ['WH1', 'WH1'],
    'Customer': ['C1', 'C2'],
    'Order Cost': [10, 12],
    'Avg. Lead Time': [3, 4],
    'St. Dev. Lead Time': [1, 1.5]
}
network_df = pd.DataFrame(network_data)
st.write("### Network Configuration")
st.data_editor(network_df, num_rows='dynamic')

# Compute Safety Stock, Reorder Point, and EOQ
echelon2_df['Safety Stock'] = echelon2_df.apply(lambda row: calculate_safety_stock(
    row['St. Dev. Demand'], 
    network_df.loc[network_df['Customer'] == row['Customer'], 'Avg. Lead Time'].values[0],
    network_df.loc[network_df['Customer'] == row['Customer'], 'St. Dev. Lead Time'].values[0],
    row['Service Level']), axis=1)

echelon2_df['Reorder Point'] = echelon2_df.apply(lambda row: calculate_reorder_point(
    row['Avg. Demand'],
    network_df.loc[network_df['Customer'] == row['Customer'], 'Avg. Lead Time'].values[0],
    row['Safety Stock']), axis=1)

echelon2_df['EOQ'] = echelon2_df.apply(lambda row: calculate_eoq(
    row['Avg. Demand'],
    network_df.loc[network_df['Customer'] == row['Customer'], 'Order Cost'].values[0],
    row['Holding $/Unit']), axis=1)

st.write("### Calculated Inventory Levels")
st.dataframe(echelon2_df[['Customer', 'Safety Stock', 'Reorder Point', 'EOQ']])

# Simulation of inventory over time per customer with demand and lead time variability
fig, ax = plt.subplots(figsize=(10, 6))
customer_inventory = {customer: [] for customer in echelon2_df['Customer']}
customer_current_inventory = echelon2_df.set_index('Customer')['Reorder Point'].to_dict()
customer_order_quantity = echelon2_df.set_index('Customer')['EOQ'].to_dict()
order_pending = {customer: False for customer in echelon2_df['Customer']}
lead_time_remaining = {customer: 0 for customer in echelon2_df['Customer']}

total_inventory_levels = []

for day in range(simulation_days):
    total_inventory = 0
    for customer in customer_inventory.keys():
        customer_inventory[customer].append(customer_current_inventory[customer])
        total_inventory += customer_current_inventory[customer]
        
        if order_pending[customer]:
            lead_time_remaining[customer] -= 1
            if lead_time_remaining[customer] <= 0:
                customer_current_inventory[customer] += customer_order_quantity[customer]
                order_pending[customer] = False
        
        daily_demand = np.random.normal(
            echelon2_df.loc[echelon2_df['Customer'] == customer, 'Avg. Demand'].values[0],
            echelon2_df.loc[echelon2_df['Customer'] == customer, 'St. Dev. Demand'].values[0]
        )
        
        customer_current_inventory[customer] = max(0, customer_current_inventory[customer] - daily_demand)
        
        if customer_current_inventory[customer] <= echelon2_df.loc[echelon2_df['Customer'] == customer, 'Reorder Point'].values[0] and not order_pending[customer]:
            order_pending[customer] = True
            lead_time_remaining[customer] = int(np.random.normal(
                network_df.loc[network_df['Customer'] == customer, 'Avg. Lead Time'].values[0],
                network_df.loc[network_df['Customer'] == customer, 'St. Dev. Lead Time'].values[0]
            ))
    
    total_inventory_levels.append(total_inventory)

for customer, inventory_levels in customer_inventory.items():
    ax.plot(range(simulation_days), inventory_levels, label=f"{customer} Inventory")

ax.set_title("Inventory Over Time Per Customer")
ax.set_xlabel("Days")
ax.set_ylabel("Inventory Level")
ax.legend()
st.pyplot(fig)

# Visualization of total inventory over time
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(range(simulation_days), total_inventory_levels, label="Total Inventory Over Time", marker='o')
ax.set_title("Total Inventory in System Over Time")
ax.set_xlabel("Days")
ax.set_ylabel("Total Inventory")
ax.legend()
st.pyplot(fig)

st.write("Use the sidebar to adjust parameters and see the impact on inventory allocation, safety stock levels, and order quantities.")