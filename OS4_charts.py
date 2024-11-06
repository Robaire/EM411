# Robaire Galliath
# EM 411, Fall 2024

import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgb
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

SINGLES = "./Q4/singles.csv"
PAIRS = "./Q4/pairs.csv"
REFERENCE = "./Q4/reference.csv"
POINTS = "./Q4/points.csv"
MAX_COST = 1_000_000

results = []
for s in [SINGLES, PAIRS, REFERENCE, POINTS]:
    data = pd.read_csv(s)
    data = data.loc[data["fleet_cost"] < MAX_COST]
    data["vehicles"] = data["vehicles"].apply(ast.literal_eval)
    data["vehicle_quantities"] = data["vehicle_quantities"].apply(ast.literal_eval)
    data["vehicle_costs"] = data["vehicle_costs"].apply(ast.literal_eval)
    data["vehicle_ranges"] = data["vehicle_ranges"].apply(ast.literal_eval)
    data["vehicle_speeds"] = data["vehicle_speeds"].apply(ast.literal_eval)
    data["fleet_size"] = data["vehicle_quantities"].apply(sum)
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
points = results[3]

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
    s=80,
)
plt.annotate(
    "Reference",  # Text label
    (
        reference["fleet_cost"][0] / 1_000_000,
        reference["utility"][0],
    ),  # Point to annotate
    textcoords="offset points",  # Position the text
    xytext=(7, 7),  # Offset from the point (x, y) in pixels
    ha="left",  # Horizontal alignment
    va="center",
    fontweight="bold",
    color=to_rgb("C3"),  # Color of the label
)
ax.scatter(
    pareto["fleet_cost"] / 1_000_000,
    pareto["utility"],
    marker=".",
    label="Pareto",
    alpha=1.0,
)
ax.scatter(
    points["fleet_cost"] / 1_000_000,
    points["utility"],
    marker="*",
    label="Points",
    alpha=1.0,
    s=80,
    color=to_rgb("C5"),
)

for i, p in points.iterrows():
    ax.annotate(
        f"Point {i+1}",
        (p["fleet_cost"] / 1_000_000, p["utility"]),
        textcoords="offset points",
        xytext=(-5, 10),
        ha="right",
        va="center",
        fontweight="bold",
        color=to_rgb("C5"),
    )

markers = [
    Line2D([0], [0], color=to_rgb("C0"), marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C1"), marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C2"), marker=".", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C4"), marker=".", linestyle="", alpha=1.0),
]
ax.legend(
    markers,
    ["Bikes", "Cars", "Pairs", "Pareto"],
    loc="upper left",
    bbox_to_anchor=(0, 0.92),
)
plt.scatter([0], [1], color="magenta", marker="*", s=100, label="Utopia Point")
plt.annotate(
    "Utopia Point",  # Text label
    (0, 1),  # Point to annotate
    textcoords="offset points",  # Position the text
    xytext=(10, 0),  # Offset from the point (x, y) in pixels
    ha="left",  # Horizontal alignment
    va="center",
    fontweight="bold",
    color="magenta",  # Color of the label
)
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
    alpha=1,
    s=80,
)

plt.annotate(
    "Reference",  # Text label
    (
        reference["fleet_cost"][0] / 1_000_000,
        reference["utility"][0],
    ),  # Point to annotate
    textcoords="offset points",  # Position the text
    xytext=(7, 7),  # Offset from the point (x, y) in pixels
    ha="left",  # Horizontal alignment
    va="center",
    fontweight="bold",
    color=to_rgb("C3"),  # Color of the label
)
ax.scatter(
    points["fleet_cost"] / 1_000_000,
    points["utility"],
    marker="*",
    alpha=1.0,
    s=80,
    color=to_rgb("C5"),
)

for i, p in points.iterrows():
    ax.annotate(
        f"Point {i+1}",
        (p["fleet_cost"] / 1_000_000, p["utility"]),
        textcoords="offset points",
        xytext=(-5, 10),
        ha="right",
        va="center",
        fontweight="bold",
        color=to_rgb("C5"),
    )
plt.scatter([0], [1], color="magenta", marker="*", s=100)
plt.annotate(
    "Utopia Point",  # Text label
    (0, 1),  # Point to annotate
    textcoords="offset points",  # Position the text
    xytext=(10, 0),  # Offset from the point (x, y) in pixels
    ha="left",  # Horizontal alignment
    va="center",
    fontweight="bold",
    color="magenta",  # Color of the label
)
ax.legend(
    loc="upper left",
    bbox_to_anchor=(0, 0.92),
)
plt.savefig("pareto_front.png")

# Save Pareto Front into a separate CSV
pareto.to_csv("pareto_front.csv")

# Plot by fleet size
fig, ax = plt.subplots()
ax.set_xlabel("Cost [$M]")
ax.set_ylabel("Utility [1]")
ax.set_title("Architecture Performance")

filt = data.loc[data["utility"] > 0.8]

bin_edges = np.linspace(0, 120, 7)
bins = np.digitize(filt["fleet_size"], bin_edges)
colors = plt.cm.tab10(np.linspace(0, 1, len(bin_edges)))
cmap = mcolors.ListedColormap(colors)

sc = ax.scatter(
    filt["fleet_cost"] / 1_000_000,
    filt["utility"],
    c=bins,
    cmap=cmap,
    vmin=1,
    vmax=len(bin_edges),
    label="Architectures",
    marker=".",
    s=5,
    alpha=1,
)

handles = []
for i in range(len(bin_edges) - 1):
    label = f"{int(bin_edges[i])} - {int(bin_edges[i+1])}"
    color = colors[i]
    patch = mpatches.Patch(color=color, label=label)
    handles.append(patch)

plt.legend(handles=handles, title="Fleet Size", loc="upper left")

# plt.colorbar(sc, label="Fleet Size", ticks=range(0, len(bin_edges) + 1))
plt.show()
