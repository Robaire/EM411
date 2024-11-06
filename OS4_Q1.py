# Robaire Galliath
# EM 411, Fall 2024

from mvu import Utility, MVU
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgb
import numpy as np

# Single Variate Utility Functions
volume = Utility([0, 500, 1000, 1500, 2000], [0, 0.2, 0.4, 0.8, 1.0])
throughput = Utility([0, 50, 100, 150, 200], [0, 0.2, 0.5, 0.9, 1.0])
wait_time = Utility([0, 5, 10, 15, 20, 30], [1.0, 0.95, 0.75, 0.4, 0.2, 0])
availability = Utility([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
utilities = [volume, throughput, wait_time, availability]

# Weights
weights = [0.15, 0.25, 0.35, 0.25]

mvu = MVU(utilities, weights)

# Print Results
a = [1000, 75, 8, 0.7]
b = [2000, 100, 12, 0.6]
c = [750, 75, 6, 0.8]
print(f"Case A: {mvu.evaluate(a)}")
print(f"Case B: {mvu.evaluate(b)}")
print(f"Case C: {mvu.evaluate(c)}")

# TODO: Print graphs of each function to validate its behavior
# Each function needs to be bounded (1, 0) and monotonic
fig, ax = plt.subplots(nrows=2, ncols=2)

ax[0, 0].set_title("Volume")
ax[0, 0].set_ylabel("Utility [1]")
ax[0, 0].set_xlabel("Total Passenger Volume [pax/day]")
x = np.linspace(-200, 2200, 1000)
ax[0, 0].plot(x, volume.util(x), zorder=0)
ax[0, 0].scatter([a[0]], [volume.util(a[0])], label="A")
ax[0, 0].scatter([b[0]], [volume.util(b[0])], label="B")
ax[0, 0].scatter([c[0]], [volume.util(c[0])], label="C")

ax[1, 0].set_title("Throughput")
ax[1, 0].set_ylabel("Utility [1]")
ax[1, 0].set_xlabel("Max Passenger Throughput [pax/hr]")
x = np.linspace(-20, 220, 1000)
ax[1, 0].plot(x, throughput.util(x), zorder=0)
ax[1, 0].scatter([a[1]], [throughput.util(a[1])], label="A")
ax[1, 0].scatter([b[1]], [throughput.util(b[1])], label="B")
ax[1, 0].scatter([c[1]], [throughput.util(c[1])], marker="x", label="C")

ax[0, 1].set_title("Wait Time")
ax[0, 1].set_xlabel("Wait Time [min]")
x = np.linspace(-5, 35, 1000)
ax[0, 1].plot(x, wait_time.util(x), zorder=0)
ax[0, 1].scatter([a[2]], [wait_time.util(a[2])], label="A")
ax[0, 1].scatter([b[2]], [wait_time.util(b[2])], label="B")
ax[0, 1].scatter([c[2]], [wait_time.util(c[2])], label="C")

ax[1, 1].set_title("Availability")
ax[1, 1].set_xlabel("Availability [%]")
x = np.linspace(-0.2, 1.2, 1000)
ax[1, 1].plot(x, availability.util(x), zorder=0)
ax[1, 1].scatter([a[3]], [availability.util(a[3])], label="A")
ax[1, 1].scatter([b[3]], [availability.util(b[3])], label="B")
ax[1, 1].scatter([c[3]], [availability.util(c[3])], label="C")

markers = [
    Line2D([0], [0], color=to_rgb("C0"), marker="o", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C1"), marker="o", linestyle="", alpha=1.0),
    Line2D([0], [0], color=to_rgb("C2"), marker="o", linestyle="", alpha=1.0),
]
fig.legend(markers, ["A", "B", "C"], loc=[0.87, 0.77])

plt.tight_layout()
plt.savefig("mvu_validation.png")
plt.show()
