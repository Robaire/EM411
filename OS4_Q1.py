# Robaire Galliath
# EM 411, Fall 2024

import numpy as np
import math
from dataclasses import dataclass


@dataclass
class Utility:
    attribute: list[float]
    utility: list[float]

    def util(self, x):
        return np.interp(x, self.attribute, self.utility)


class MVU:
    utilities: list[Utility]
    weights: list[float]

    def __init__(self, utilities, weights):

        if not math.isclose(np.sum(weights), 1):
            raise ValueError("Weights must sum to 1")

        if len(utilities) != len(weights):
            raise ValueError(
                "Utilities and Weights must have the same number of elements"
            )

        self.utilities = utilities
        self.weights = weights

    def evaluate(self, attributes):

        if len(attributes) != len(self.utilities):
            raise ValueError(f"Attributes must be length {len(self.utilities)}")

        return np.dot(
            [u.util(a) for a, u in zip(attributes, self.utilities)], self.weights
        )


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
