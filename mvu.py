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
        """Return the utility [1]."""

        if len(attributes) != len(self.utilities):
            raise ValueError(f"Attributes must be length {len(self.utilities)}")

        return np.dot(
            [u.util(a) for a, u in zip(attributes, self.utilities)], self.weights
        )
