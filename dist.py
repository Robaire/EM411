import random
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np

N = 100
dist = lambda: round(random.gauss(5, 1))

data = np.zeros(N)
for i in range(N):
    data[i] = dist()

fig, ax = plt.subplots()
d = np.diff(np.unique(data)).min()
left_of_first_bin = data.min() - float(d) / 2
right_of_last_bin = data.max() + float(d) / 2
plt.hist(
    data,
    np.arange(left_of_first_bin, right_of_last_bin + d, d),
    weights=np.ones(len(data)) / len(data),
)

ax.set_title("Trip Length Distribution")
ax.set_xlabel("Trip Length")
ax.set_ylabel("Probability")

plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
plt.savefig("distribution.png")
plt.show()
