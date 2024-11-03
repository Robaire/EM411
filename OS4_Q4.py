# Robaire Galliath
# EM 411, Fall 2024

from designs import *
from transport import *
from multiprocessing import Pool
from copy import deepcopy
import csv
import time
import math
import random
import itertools

####################################################
# Stochastic Model of Transport System Performance #
####################################################

# System Scenario 2 #
# ----------------- #
# Assumptions:
#   - All trips originate at Kendall/MIT
#   - Trips have an average distance of 1.5 km, std-dev 0.4km
#   - 1% of trips have an average distance of 10 km, std-dev 1 km (representing rides outside the boundary like to Logan)
#   - Vehicles return to Kendall/MIT after dropping off passengers
#   - Trips have 1-8 passengers but most rides are about 3 people
#   - Speed limit kn surface streets is 40 kph (~25 mph)
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
def DISTANCE():
    return random.choices(
        [random.gauss(1.5, 0.4), random.gauss(10, 1)], weights=[99, 1], k=1
    )[0]


# Passenger Model
def PASSENGERS():
    a = max(round(random.lognormvariate(0.2, 0.2)), 1)
    b = max(round(random.gauss(4, 1)), 1)
    return random.choices([a, b], weights=[40, 60], k=1)[0]


# Demand Model
# DEMAND_ADJUST = lambda x: random.gauss(x, x * 0.05)  # std-dev 5% of mean
DEMAND_ADJUST = lambda x: x

# Demand over a 24 hour period, evenly spaced
DEMAND = [15, 5, 15, 50, 150, 150, 150, 100, 75, 100, 50, 35]
DEMAND = [d for d in DEMAND for _ in (0, 1)]
# DEMAND = [5000]  # Saturating demand

MAX_WAIT = 20 / 60  # [hr] maximum wait allowed for a ride request or its dropped
AVAILABILITY = 1  # [min] availability threshold
DWELL_TIME = 2 / 60  # [hr] (two minutes)
CHARGE_DISTANCE = 5  # [km] start charging when range drops below this value
CHARGE_TIME_PENALTY = 0.25  # [hr] fixed time penalty for charging

COST_CAP = 1_000_000  # [$] fleet cost cap


#################
# Design Vector #
#################
if __name__ == "__main__":  # Necessary for multiprocessing

    # Create the simulator
    sim = Simulation(
        MAX_WAIT, AVAILABILITY, DWELL_TIME, CHARGE_DISTANCE, CHARGE_TIME_PENALTY
    )

    # Randomly generate a list of ride requests over a 24 hour period
    rides: list[Ride] = []
    for i, demand in enumerate(DEMAND):
        interval = 24 / len(DEMAND)

        for _ in range(math.ceil(DEMAND_ADJUST(demand))):
            ride_time = random.uniform(i * interval, (i + 1) * interval)
            rides.append(Ride(DISTANCE(), PASSENGERS(), ride_time))

    # Sort rides by start time
    rides = sorted(rides, key=lambda x: x.start_time)

    def copy_rides(rides):
        """Create a deep copy."""
        result: list[Ride] = [None] * len(rides)
        for i, r in enumerate(rides):
            result[i] = deepcopy(r)
        return result

    # Bicycle Generator
    def bike_gen():
        for b in itertools.product(
            bike_frames.values(),
            bike_batteries.values(),
            bike_chargers.values(),
            bike_motors.values(),
        ):
            try:
                yield Bicycle.from_tuple(b)
            except ValueError:
                continue

    # Car Generator
    def car_gen():
        for c in itertools.product(
            car_chassis.values(),
            car_batteries.values(),
            car_chargers.values(),
            car_motors.values(),
            car_autonomy.values(),
        ):
            try:
                yield RoadVehicle.from_tuple(c)
            except ValueError:
                continue

    def single_gen(iter):
        for v, q in iter:
            fleet = Fleet([v], [q])
            if fleet.cost() <= COST_CAP:
                yield (fleet, copy_rides(rides))

    def double_gen(iter):
        for i in iter:
            fleet = Fleet([i[0][0], i[1][0]], [i[0][1], i[1][1]])
            if fleet.cost() <= COST_CAP:
                yield (fleet, copy_rides(rides))

    # Calculate References
    fleets: list[Fleet] = []
    fleets.append(Fleet([bike_design("B2E1G2K3"), car_design("C3P1G1M1A3")], [50, 10]))
    results = list(map(sim.run, [(f, copy_rides(rides)) for f in fleets]))

    with open("references.csv", "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(vars(results[0]).keys())  # Headers
        for r in results:
            writer.writerow(vars(r).values())

    # Calculate Singles
    bikes = itertools.product(bike_gen(), range(40, 101, 10))
    cars = itertools.product(car_gen(), range(8, 21, 2))
    singles = itertools.chain.from_iterable([bikes, cars])

    start_time = time.time()
    with Pool(16) as p:
        results_single: list[Result] = p.map(sim.run, single_gen(singles))
    elapsed = time.time() - start_time
    print(f"Compute time: {elapsed / 60:.3f} minutes")
    print(f"Results: {len(results_single)}")

    with open("singles.csv", "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(vars(results_single[0]).keys())  # Headers
        for r in results_single:
            writer.writerow(vars(r).values())

    # Reduce the design space
    del car_chassis["C5"]
    del car_chassis["C6"]
    del car_chassis["C7"]
    del car_chassis["C8"]
    del car_batteries["P5"]
    del car_batteries["P6"]
    del car_batteries["P7"]
    del car_chargers["G3"]
    del car_motors["M4"]
    del car_autonomy["A4"]
    del car_autonomy["A5"]

    del bike_chargers["G1"]
    del bike_motors["K1"]
    del bike_motors["K2"]

    # Calculate Pairs
    bikes = itertools.product(bike_gen(), range(40, 101, 10))
    cars = itertools.product(car_gen(), range(8, 21, 2))
    pairs = itertools.product(bikes, cars)

    start_time = time.time()
    with Pool(16) as p:
        results_pairs: list[Result] = p.map(sim.run, double_gen(pairs))
    elapsed = time.time() - start_time
    print(f"Compute time: {elapsed / 60:.3f} minutes")
    print(f"Results: {len(results_pairs)}")

    with open("pairs.csv", "w", newline="") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(vars(results_pairs[0]).keys())  # Headers
        for r in results_pairs:
            writer.writerow(vars(r).values())
