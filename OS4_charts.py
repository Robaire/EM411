# Robaire Galliath
# EM 411, Fall 2024

import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgb

SINGLES = "./Q4/singles.csv"
PAIRS = "./Q4/pairs.csv"
REFERENCE = "./Q4/reference.csv"
MAX_COST = 1_000_000

results = []
for s in [SINGLES, PAIRS, REFERENCE]:
    data = pd.read_csv(s)
    data = data.loc[data["fleet_cost"] < MAX_COST]
    data["vehicles"] = data["vehicles"].apply(ast.literal_eval)
    data["vehicle_quantities"] = data["vehicle_quantities"].apply(ast.literal_eval)
    data["vehicle_costs"] = data["vehicle_costs"].apply(ast.literal_eval)
    data["vehicle_ranges"] = data["vehicle_ranges"].apply(ast.literal_eval)
    data["vehicle_speeds"] = data["vehicle_speeds"].apply(ast.literal_eval)
    results.append(data)

data = pd.concat(results)


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

singles = results[0]
pairs = results[1]
reference = results[2]

# Classify into Bikes and Cars
singles["class"] = singles["vehicles"].apply(lambda x: x[0][0])
bikes = singles.loc[singles["class"] == "B"]
cars = singles.loc[singles["class"] == "C"]

# Plot Performance
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Architecture Performance")
ax.scatter(
    bikes["fleet_cost"] / 1_000_000,
    bikes["utility"],
    marker=".",
    label="Bikes",
    alpha=0.2,
)
ax.scatter(
    cars["fleet_cost"] / 1_000_000,
    cars["utility"],
    marker=".",
    label="Cars",
    alpha=0.2,
)
ax.scatter(
    pairs["fleet_cost"] / 1_000_000,
    pairs["utility"],
    marker=".",
    label="Pairs",
    alpha=0.2,
)
ax.scatter(
    reference["fleet_cost"] / 1_000_000,
    reference["utility"],
    marker="*",
    label="Reference",
    alpha=1,
)
ax.scatter(
    pareto["fleet_cost"] / 1_000_000,
    pareto["utility"],
    marker=".",
    label="Pareto",
    alpha=1.0,
)
plt.annotate(
    "Utopia Point",  # Text label
    (0, 1),  # Point to annotate
    textcoords="offset points",  # Position the text
    xytext=(10, 0),  # Offset from the point (x, y) in pixels
    ha="left",  # Horizontal alignment
    va="center",
    color="red",  # Color of the label
)
markers = [
    Line2D([0], [0], color=to_rgb("C0"), marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C1"), marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C2"), marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C3"), marker="*", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C4"), marker=".", linestyle="", alpha=1.0),
]
ax.legend(
    markers,
    ["Bikes", "Cars", "Pairs", "Reference", "Pareto"],
    loc="upper left",
    bbox_to_anchor=(0, 0.92),
)
plt.scatter([0], [1], color="red", marker="*", s=100, label="Utopia Point")
plt.savefig("performance.png")

bikes = bikes.sort_values("fleet_cost")
p_bikes = bikes.loc[is_pareto(bikes["utility"])]

cars = cars.sort_values("fleet_cost")
p_cars = cars.loc[is_pareto(cars["utility"])]

pairs = pairs.sort_values("fleet_cost")
p_pairs = pairs.loc[is_pareto(pairs["utility"])]

# Plot Pareto Fronts
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Pareto Fronts")
ax.scatter(
    p_bikes["fleet_cost"] / 1_000_000,
    p_bikes["utility"],
    marker=".",
    label="Bikes",
)
ax.scatter(
    p_cars["fleet_cost"] / 1_000_000,
    p_cars["utility"],
    marker=".",
    label="Cars",
)
ax.scatter(
    p_pairs["fleet_cost"] / 1_000_000,
    p_pairs["utility"],
    marker=".",
    label="Pairs",
)
ax.scatter(
    reference["fleet_cost"] / 1_000_000,
    reference["utility"],
    marker="*",
    label="Reference",
    alpha=1,
)

ax.legend()
plt.savefig("pareto_front.png")

# Save Pareto Front into a separate CSV
pareto.to_csv("pareto_front.csv")
