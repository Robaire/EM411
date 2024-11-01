# Robaire Galliath
# EM 411, Fall 2024

import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

INPUT = "./results.csv"

data = pd.read_csv(INPUT)

# Reformat Data
data["vehicles"] = data["vehicles"].apply(ast.literal_eval)
data["vehicle_quantities"] = data["vehicle_quantities"].apply(ast.literal_eval)
data["vehicle_costs"] = data["vehicle_costs"].apply(ast.literal_eval)
data["vehicle_ranges"] = data["vehicle_ranges"].apply(ast.literal_eval)
data["vehicle_speeds"] = data["vehicle_speeds"].apply(ast.literal_eval)

# Classify into Bikes and Cars
data["class"] = data["vehicles"].apply(lambda x: x[0][0] + x[1][0])
bikes = data.loc[data["class"] == "BB"]
cars = data.loc[data["class"] == "CC"]
bikes_cars = data.loc[data["class"] != "BB"].loc[data["class"] != "CC"]

# Plot
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Architecture Performance")
# ax.scatter(
#    bikes["fleet_cost"] / 1_000_000,
#    bikes["utility"],
#    marker=".",
#    label="Bike-Bike",
#    alpha=0.1,
# )
# ax.scatter(
#    cars["fleet_cost"] / 1_000_000,
#    cars["utility"],
#    marker=".",
#    label="Car-Car",
#    alpha=0.1,
# )
ax.scatter(
    bikes_cars["fleet_cost"] / 1_000_000,
    bikes_cars["utility"],
    marker=".",
    label="Bike-Car",
    alpha=0.1,
)
markers = [
    Line2D([0], [0], color="#1f77b4", marker=".", linestyle="", alpha=1.0),
    # Line2D([0], [0], color="#ff7f0e", marker=".", linestyle="", alpha=1.0),
    # Line2D([0], [0], color="#2ca02c", marker=".", linestyle="", alpha=1.0),
]
# ax.legend(markers, ["Bike-Bike", "Car-Car", "Bike-Car"])
ax.legend(markers, ["Bike-Car"], loc="lower right")
plt.savefig("architecture_performance.png")


# Isolate pareto front
def is_pareto(utility):
    """Assumes the input is sorted by cost."""
    is_efficient = np.ones(utility.shape[0], dtype=bool)
    for i, u in enumerate(utility):
        is_efficient[i] = not np.any(utility[:i] >= u)
    return is_efficient


# Sort entries by cost
data = data.sort_values("fleet_cost")
pareto = data.loc[is_pareto(data["utility"])]

# Classify into Bikes and Cars
p_bikes = pareto.loc[pareto["class"] == "BB"]
p_cars = pareto.loc[pareto["class"] == "CC"]
p_bikes_cars = pareto.loc[pareto["class"] != "BB"].loc[pareto["class"] != "CC"]

# Plot
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Pareto Front")
# ax.scatter(
#    bikes["fleet_cost"] / 1_000_000,
#    bikes["utility"],
#    marker=".",
#    label="Bike-Bike",
#    alpha=1,
# )
# ax.scatter(
#    cars["fleet_cost"] / 1_000_000,
#    cars["utility"],
#    marker=".",
#    label="Car-Car",
#    alpha=1,
# )
ax.scatter(
    bikes_cars["fleet_cost"] / 1_000_000,
    bikes_cars["utility"],
    marker=".",
    label="Bike-Car",
    alpha=0.1,
)
ax.scatter(
    p_bikes_cars["fleet_cost"] / 1_000_000,
    p_bikes_cars["utility"],
    marker=".",
    label="Pareto",
    alpha=1,
)
markers = [
    Line2D([0], [0], color="#1f77b4", marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color="#ff7f0e", marker=".", linestyle="", alpha=1.0),
    # Line2D([0], [0], color="#2ca02c", marker=".", linestyle="", alpha=1.0),
]
ax.legend(markers, ["Bike-Car", "Pareto"], loc="lower right")
plt.savefig("pareto_front.png")

# Save Pareto Front into a separate CSV
pareto.to_csv("pareto_front.csv")
