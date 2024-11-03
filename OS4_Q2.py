# Robaire Galliath
# EM 411, Fall 2024

from designs import *
from transport import *
from copy import deepcopy
import csv
import time
import math
import random

####################################################
# Stochastic Model of Transport System Performance #
####################################################

# System Scenario 1 #
# ----------------- #
# Assumptions:
#   - All trips originate at Kendall/MIT
#   - Trips have an average distance of 1.5 km, std-dev 0.4km
#   - Vehicles return to Kendall/MIT after dropping off passengers
#   - Trips have 1-6 passengers
#   - Speed limit on surface streets is 40 kph (~25 mph)
#   - Speed limit for bikes is 15 kph (~10 mph)
#
# Model Approach:
#   - Assume a uniform distribution of ride requests over each hour
#   - Use a probability model to determine the parameters of the ride requested (# passengers, distance)

#######################
# Model Configuration #
#######################
random.seed("EM411")  # Seed the RNG

# Distance Model
DISTANCE = lambda: random.gauss(1.5, 0.4)  # 1.5 km average, 0.4 km std-dev

# Passenger Model
PASSENGERS = lambda: max(round(random.lognormvariate(0.2, 0.5)), 1)

# Demand over a 24 hour period, evenly spaced
DEMAND = [15, 5, 15, 50, 150, 150, 150, 100, 75, 100, 50, 35]
DEMAND = [d for d in DEMAND for _ in (0, 1)]

MAX_WAIT = 10 / 60  # [hr] maximum wait allowed for a ride request or its dropped
AVAILABILITY = 1  # [min] availability threshold
DWELL_TIME = 1 / 60  # [hr] (one minute)
CHARGE_DISTANCE = 5  # [km] start charging when range drops below this value
CHARGE_TIME_PENALTY = 0.25  # [hr] fixed time penalty for charging

#################
# Design Vector #
#################
if __name__ == "__main__":  # Necessary for multiprocessing

    # Create the simulator
    sim = Simulation(
        MAX_WAIT, AVAILABILITY, DWELL_TIME, CHARGE_DISTANCE, CHARGE_TIME_PENALTY
    )

    # Construct Five Notional Architectures
    fleets: list[Fleet] = []
    fleets.append(
        Fleet([bike_design("B2E1G2K3"), car_design("C3P1G1M1A3")], [50, 10])
    )  # Robaire
    fleets.append(Fleet([car_design("C4P4G2M3A3")], [12]))  # Robaire
    fleets.append(
        Fleet([bike_design("B1E1G1K2"), car_design("C2P3G3M3A3")], [50, 10])
    )  # Lisa
    fleets.append(Fleet([bike_design("B3E3G2K3")], [100]))  # Azusa
    fleets.append(
        Fleet([bike_design("B1E1G2K3"), car_design("C3P2G2M4A3")], [50, 10])
    )  # Morgan

    # Randomly generate a list of ride requests over a 24 hour period
    rides: list[Ride] = []
    for i, demand in enumerate(DEMAND):
        interval = 24 / len(DEMAND)

        for _ in range(math.ceil(demand)):
            ride_time = random.uniform(i * interval, (i + 1) * interval)
            rides.append(Ride(DISTANCE(), PASSENGERS(), ride_time))

    rides = sorted(rides, key=lambda x: x.start_time)

    def copy_rides(rides):
        """Create a deep copy."""
        result: list[Ride] = [None] * len(rides)
        for i, r in enumerate(rides):
            result[i] = deepcopy(r)
        return result

    # Run the simulation
    start_time = time.time()
    results = list(map(sim.run, [(f, copy_rides(rides)) for f in fleets]))
    elapsed = time.time() - start_time
    print(f"Compute time: {elapsed / 60:.3f} minutes")
    print(f"Results: {len(results)}")

    # Save the results in a CSV
    with open("results.csv", "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(vars(results[0]).keys())  # Write Headers
        for r in results:
            writer.writerow(vars(r).values())
