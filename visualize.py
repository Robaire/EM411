# Robaire galliath
# EM 411, Fall 2024

import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

INPUT = "./all_single_vehicles/all_single_vehicles.csv"

data = pd.read_csv(INPUT)

# Reformat Data
data["vehicles"] = data["vehicles"].apply(ast.literal_eval)
data["vehicle_quantities"] = data["vehicle_quantities"].apply(ast.literal_eval)
data["vehicle_costs"] = data["vehicle_costs"].apply(ast.literal_eval)
data["vehicle_ranges"] = data["vehicle_ranges"].apply(ast.literal_eval)
data["vehicle_speeds"] = data["vehicle_speeds"].apply(ast.literal_eval)

# Classify into Bikes and Cars
data["class"] = data["vehicles"].apply(lambda x: x[0][0])
bikes = data.loc[data["class"] == "B"]
cars = data.loc[data["class"] == "C"]

# Plot
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Architecture Performance")
ax.scatter(bikes["fleet_cost"] / 1_000_000, bikes["utility"], marker=".", alpha=0.4)
ax.scatter(cars["fleet_cost"] / 1_000_000, cars["utility"], marker=".", alpha=0.4)
ax.legend(["Bike", "Car"])
plt.savefig("architecture_performance.png")


# Isolate pareto front
def is_pareto(utility):
    """Assumes the input is sorted by cost."""
    is_efficient = np.ones(utility.shape[0], dtype=bool)
    for i, u in enumerate(utility):
        is_efficient[i] = not np.any(utility[:i] > u)
    return is_efficient


# Sort entries by cost
data = data.sort_values("fleet_cost")
pareto = data.loc[is_pareto(data["utility"])]

# Classify into Bikes and Cars
bikes = pareto.loc[pareto["class"] == "B"]
cars = pareto.loc[pareto["class"] == "C"]

# Plot
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Pareto Front")
ax.scatter(bikes["fleet_cost"] / 1_000_000, bikes["utility"], marker=".")
ax.scatter(cars["fleet_cost"] / 1_000_000, cars["utility"], marker=".")
ax.legend(["Bike", "Car"])
plt.savefig("pareto_front.png")
