# Robaire Galliath
# EM 411, Fall 2024


from dataclasses import dataclass
from mvu import MVU, Utility
from designs import *
from vehicle import _Vehicle
from multiprocessing import Pool
import csv
import itertools
import math
import random
import time
from copy import deepcopy

# Single Variate Utility Functions
mvu_volume = Utility([0, 500, 1000, 1500, 2000], [0, 0.2, 0.4, 0.8, 1.0])
mvu_throughput = Utility([0, 50, 100, 150, 200], [0, 0.2, 0.5, 0.9, 1.0])
mvu_wait_time = Utility([0, 5, 10, 15, 20, 30], [1.0, 0.95, 0.75, 0.4, 0.2, 0])
mvu_availability = Utility([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
mvu_utilities = [mvu_volume, mvu_throughput, mvu_wait_time, mvu_availability]
mvu_weights = [0.15, 0.25, 0.35, 0.25]  # Weights
mvu = MVU(mvu_utilities, mvu_weights)


# Class for tracking vehicle state
class RealVehicle:
    vehicle: _Vehicle
    battery_capacity: float  # Current battery charge [kWh]
    next_available: float = 0  # The time this vehicle becomes available [hr]

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.battery_capacity = self.vehicle.battery.capacity

    def range(self):
        """Current range [km]."""
        return (self.battery_capacity * 1000) / self.vehicle.power_consumption()

    def move(self, distance):
        """Decrease the battery capacity for a distance traveled in km."""
        self.battery_capacity -= (self.vehicle.power_consumption() * distance) / 1000
        return self.battery_capacity

    def charge_time(self):
        """Time to charge from current capacity to full [hr]"""
        return (
            self.vehicle.battery.capacity - self.battery_capacity
        ) / self.vehicle.charger.power


# For tracking ride state
@dataclass
class Ride:
    distance: float  # One way ride distance
    passengers: int  # Passenger count
    start_time: float  # When the request begins [hr]
    filled_time: float = -1  # When the request is filled [hr]
    complete_time: float = -1  # When the ride is completed [hr]

    def wait_time(self):
        """Wait time [hr]."""
        return self.filled_time - self.start_time

    def travel_time(self):
        """Travel time [hr]."""
        return self.complete_time - self.filled_time


class Result:
    vehicles: list[str]
    vehicle_quantities: list[int]
    vehicle_costs: list[float]
    vehicle_ranges: list[float]
    vehicle_speeds: list[float]

    total_requests: int
    completed: int
    dropped: int
    impossible: int
    pax_volume: int
    pax_max: int
    average_wait: float
    max_wait: float
    average_duration: float
    average_distance: float
    availability: float
    utility: float
    fleet_cost: float

    def __init__(self, rides: list[Ride], vehicles: list[RealVehicle], fleet: Fleet):
        self.vehicles = [v.design() for v in fleet.vehicles]
        self.vehicle_quantities = fleet.quantities
        self.vehicle_costs = [v.cost() for v in fleet.vehicles]
        self.vehicle_ranges = [v.range() for v in fleet.vehicles]
        self.vehicle_speeds = [v.speed() for v in fleet.vehicles]

        self.total_requests = len(rides)

        completed = [r for r in rides if r.complete_time > 0.0]
        self.completed = len(completed)

        dropped = [r for r in rides if r.complete_time == -2.0]
        self.dropped = len(dropped)

        impossible = [r for r in rides if r.complete_time == -1.0]
        self.impossible = len(impossible)

        if len(rides) != len(completed) + len(dropped) + len(impossible):
            print(
                f"Rides: {len(rides)}, C: {len(completed)}, D: {len(dropped)}, I: {len(impossible)}, SUM: {len(completed) + len(dropped) + len(impossible)}"
            )

        self.pax_volume = sum([r.passengers for r in completed])

        wait_times = [r.wait_time() * 60 for r in completed]
        self.average_wait = sum(wait_times) / len(wait_times)
        self.max_wait = max(wait_times)

        trip_times = [r.travel_time() * 60 for r in completed]
        self.average_duration = sum(trip_times) / len(trip_times)

        trip_dist = [r.distance for r in completed]
        self.average_distance = sum(trip_dist) / len(trip_dist)

        self.availability = len([w for w in wait_times if w < 1]) / len(rides)

        # Search for the hour window with the highest pax volume
        pax_max = 0
        for ride in completed:
            pax = [
                r.passengers
                for r in completed
                if r.start_time > ride.start_time
                and r.complete_time <= ride.start_time + 1
            ]
            pax_max = max(sum(pax), pax_max)

        self.pax_max = pax_max
        # self.pax_max = fleet.pax_throughput(1.5)

        self.utility = mvu.evaluate(
            [self.pax_volume, pax_max, self.average_wait, self.availability]
        )

        self.fleet_cost = fleet.cost()


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
# distance = lambda: random.gauss(5, 2)  # 5 km average, 2 km std-dev
# Passenger Model
PASSENGERS = lambda: max(round(random.lognormvariate(0, 0.5)), 1)

# Demand Model
# DEMAND_ADJUST = lambda x: random.gauss(x, x * 0.05)  # std-dev 5% of mean
DEMAND_ADJUST = lambda x: x

# Demand over a 24 hour period, evenly spaced
DEMAND = [15, 5, 15, 50, 150, 150, 150, 100, 75, 100, 50, 35]
DEMAND = [d for d in DEMAND for _ in (0, 1)]
# DEMAND = [5000]  # Saturating demand

MAX_WAIT = 10 / 60  # [hr] maximum wait allowed for a ride request or its dropped
DWELL_TIME = 1 / 60  # [hr] (one minute)
CHARGE_DISTANCE = 5  # [km] start charging when range drops below this value
CHARGE_TIME_PENALTY = 0.25  # [hr] fixed time penalty for charging

COST_CAP = 1_000_000  # [$] fleet cost cap


def run_sim(args):
    """Return a Result"""

    ####################
    # Simulation Setup #
    ####################
    (fleet, rides) = args

    # Build a list of real vehicles for the simulation
    vehicles: list[RealVehicle] = []
    for v, q in zip(fleet.vehicles, fleet.quantities):
        for _ in range(q):
            vehicles.append(RealVehicle(v))

    ###################
    # Simulation Loop #
    ###################
    for ride in rides:

        # Find the next available vehicle that meets the ride criteria
        # Is this somehow messing it up?
        vehicles = sorted(
            vehicles,
            key=lambda x: (
                x.next_available,
                x.battery_capacity,
                x.vehicle.chassis.pax,
            ),
        )
        for v in vehicles:

            # Check the vehicle has enough room and distance to complete the ride
            if (
                ride.passengers <= v.vehicle.chassis.pax
                and v.range() >= ride.distance * 2
            ):

                # Check if this ride will be filled within the max wait time
                if v.next_available - ride.start_time > MAX_WAIT:
                    # Drop the ride
                    ride.complete_time = -2
                    break

                # One way travel time
                travel_time = (ride.distance / v.vehicle.speed()) + DWELL_TIME

                # Update ride parameters
                ride.filled_time = max(ride.start_time, v.next_available)
                ride.complete_time = ride.filled_time + travel_time

                # Update vehicle parameters
                v.next_available = ride.filled_time + travel_time * 2  # Availability
                v.move(ride.distance * 2)  # Update the battery charge
                if v.range() <= CHARGE_DISTANCE:
                    v.next_available += v.charge_time() + CHARGE_TIME_PENALTY
                    v.battery_capacity = v.vehicle.battery.capacity  # Reset the battery
                # Could make a decision to charge based on the availability of all other vehicles

                break

    ###################
    # Analyze Results #
    ###################
    return Result(rides, vehicles, fleet)


#################
# Design Vector #
#################
if __name__ == "__main__":  # Necessary for multiprocessing

    # Construct Five Notional Architectures
    fleets: list[Fleet] = []
    """
    # Architecture 1: 30 of the same, simple vehicle
    fleets.append(Fleet([car_design("C2P2G1M1A3")], [30]))
    # Architecture 2: 20 of a simple car, 10 of a larger car
    fleets.append(Fleet([car_design("C1P1G1M1A3"), car_design("C3P1G1M1A3")], [20, 10]))
    # Architecture 3: 30 of a large vehicle
    fleets.append(Fleet([car_design("C4P4G2M2A3")], [30]))
    # Architecture 4: 100 cheap bikes and 10 medium size vehicles
    fleets.append(Fleet([bike_design("B1E1G1K1"), car_design("C3P2G1M1A3")], [100, 10]))
    # Architecture 5: 80 fast bikes and 20 medium vehicles
    fleets.append(Fleet([bike_design("B2E1G2K3"), car_design("C3P1G1M1A3")], [80, 20]))
    """

    fleets.append(Fleet([bike_design("B1E1G2K3"), car_design("C1P1G1M2A3")], [70, 10]))
    fleets.append(Fleet([bike_design("B1E1G2K3"), car_design("C3P1G1M2A3")], [70, 10]))
    fleets.append(Fleet([bike_design("B1E1G2K3"), car_design("C1P1G1M2A3")], [70, 10]))
    fleets.append(Fleet([bike_design("B1E1G2K3"), car_design("C1P1G1M1A3")], [50, 10]))

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

    b_i = itertools.product(bike_gen(), range(40, 101, 10))
    # b_i = itertools.product(bike_gen(), [50])
    c_i = itertools.product(car_gen(), range(8, 21, 2))
    # c_i = itertools.product(car_gen(), [20])
    # i = itertools.product(itertools.chain.from_iterable([b_i, c_i]), repeat=2)

    # Compute all single vehicle fleet architectures
    # i = itertools.chain.from_iterable([b_i, c_i])

    # Compute all combinations of two vehicles
    # i = itertools.combinations(itertools.chain.from_iterable([b_i, c_i]), r=2)

    # Compute all combinations of bikes and cars
    i = itertools.product(b_i, c_i)

    # This design space at 846,951 points...
    # Compute time is approx ~1 min / 1k points
    # We know we can achieve a utility of 1.0 at a fleet cost of ~$1.15M
    # So in order to reduce the design space we will cap fleet cost at $1.2M
    # We will also only consider bike-bike and bike-car architectures (too many car-car)

    def single_gen(iter):
        for v, q in iter:
            fleet = Fleet([v], [q])
            if fleet.cost() <= COST_CAP:
                yield (fleet, copy_rides(rides))
                # yield fleet

    def double_gen(iter):
        for i in iter:
            fleet = Fleet([i[0][0], i[1][0]], [i[0][1], i[1][1]])
            if fleet.cost() <= COST_CAP:
                yield (fleet, copy_rides(rides))
                # yield fleet

    # l = 0
    # for _ in double_gen(i):
    #     l += 1
    # print(l)

    # Evolutionary algorithm...
    # Consider 100 random design points
    # Keep the top 10%
    # Replace the remaining 90% with randomly mutated variants of top 10%
    # Repeat X times
    # An issue with this is that it will just makes fleets large and expensive
    # Need to penalize cost...
    # As an alternative
    # Keep any instances on the pareto front
    # Randomly mutate to create new missing members...
    start_time = time.time()

    # Use mutliprocessing to compute in parallel
    with Pool(16) as p:
        # results: list[Result] = p.map(run_sim, [(f, copy_rides(rides)) for f in fleets])
        # results: list[Result] = p.map(run_sim, single_gen(i))
        results: list[Result] = p.map(run_sim, double_gen(i))
    # results = list(map(run_sim, double_gen(i)))
    # results = list(map(run_sim, [(f, copy_rides(rides)) for f in fleets]))

    elapsed = time.time() - start_time
    print(f"Compute time: {elapsed / 60:.3f} minutes")
    print(f"Results: {len(results)}")

    # Save the results in a CSV
    # TODO: Save the results in a pickle
    with open("results.csv", "w", newline="") as output_file:
        writer = csv.writer(output_file)

        # Print Headers
        writer.writerow(vars(results[0]).keys())

        # Print Data
        for r in results:
            writer.writerow(vars(r).values())
