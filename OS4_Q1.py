# Robaire Galliath
# EM 411, Fall 2024

from mvu import Utility, MVU

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
print(f"Case A: {mvu.evaluate([1000, 75, 8, 0.7])}")
print(f"Case B: {mvu.evaluate([2000, 100, 12, 0.6])}")
print(f"Case C: {mvu.evaluate([750, 75, 6, 0.8])}")

# TODO: Print graphs of each function to validate its behavior
# Each function needs to be bounded (1, 0) and monotonic
