# Robaire Galliath
# EM 411, Fall 2024


from dataclasses import dataclass
from mvu import MVU, Utility
from designs import *
from vehicle import _Vehicle

import math
import random

# Single Variate Utility Functions
volume = Utility([0, 500, 1000, 1500, 2000], [0, 0.2, 0.4, 0.8, 1.0])
throughput = Utility([0, 50, 100, 150, 200], [0, 0.2, 0.5, 0.9, 1.0])
wait_time = Utility([0, 5, 10, 15, 20, 30], [1.0, 0.95, 0.75, 0.4, 0.2, 0])
availability = Utility([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
utilities = [volume, throughput, wait_time, availability]
weights = [0.15, 0.25, 0.35, 0.25]  # Weights
mvu = MVU(utilities, weights)


# Class for tracking vehicle state
class RealVehicle:
    vehicle: _Vehicle
    battery_capacity: float  # Current battery charge [kWh]
    next_available: float = 0  # The time this vehicle becomes available [hr]
    ride_count: int = 0

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
    filled_time: float = None  # When the request is filled [hr]
    complete_time: float = None  # When the ride is completed [hr]

    def wait_time(self):
        """Wait time [hr]."""
        return self.filled_time - self.start_time

    def travel_time(self):
        """Travel time [hr]."""
        return self.complete_time - self.filled_time


class Result:
    vehicles: list[_Vehicle]
    fleet: Fleet
    total_requests: int
    completed: int
    dropped: int
    impossible: int
    pax_volume: int
    average_wait: float
    max_wait: float
    average_duration: float
    average_distance: float
    availability: float

    utility: float

    def __init__(self, rides, vehicles, fleet):
        self.vehicles = vehicles
        self.fleet = fleet

        self.total_requests = len(rides)

        completed = [r for r in rides if r.filled_time]
        self.completed = len(completed)

        dropped = [r for r in rides if r.complete_time == -1]
        self.dropped = len(dropped)

        impossible = [r for r in rides if not r.complete_time]
        self.impossible = len(impossible)

        self.pax_volume = sum([r.passengers for r in completed])

        wait_times = [r.wait_time() * 60 for r in completed]
        self.average_wait = sum(wait_times) / len(wait_times)
        self.max_wait = max(wait_times)

        trip_times = [r.travel_time() * 60 for r in completed]
        self.average_duration = sum(trip_times) / len(trip_times)

        trip_dist = [r.distance for r in completed]
        self.average_distance = sum(trip_dist) / len(trip_dist)

        self.availability = len([w for w in wait_times if w < 1]) / len(rides)

        self.utility = mvu.evaluate(
            [self.pax_volume, 0, self.average_wait, self.availability]
        )


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
# DEMAND = [5000]  # Saturating demand

MAX_WAIT = 10 / 60  # [hr] maximum wait allowed for a ride request or its dropped
DWELL_TIME = 1 / 60  # [hr] (one minute)
CHARGE_DISTANCE = 5  # [km] start charging when range drops below this value
CHARGE_TIME_PENALTY = 0.25  # [hr] fixed time penalty for charging


def run_sim(fleet):
    """Return a Result"""

    ####################
    # Simulation Setup #
    ####################

    # Randomly generate a list of ride requests over a 24 hour period
    rides: list[Ride] = []
    for i, demand in enumerate(DEMAND):
        interval = 24 / len(DEMAND)

        for _ in range(math.ceil(DEMAND_ADJUST(demand))):
            time = random.uniform(i * interval, (i + 1) * interval)
            rides.append(Ride(DISTANCE(), PASSENGERS(), time))

    # Sort rides by start time
    rides = sorted(rides, key=lambda x: x.start_time)

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
                if max(ride.start_time, v.next_available) - ride.start_time > MAX_WAIT:
                    # Drop the ride
                    ride.complete_time = -1
                    break

                # One way travel time
                travel_time = (ride.distance / v.vehicle.speed()) + DWELL_TIME

                # Update ride parameters
                ride.filled_time = max(ride.start_time, v.next_available)
                ride.complete_time = ride.filled_time + travel_time

                # Update vehicle parameters
                v.next_available = ride.filled_time + travel_time * 2  # Availability
                v.ride_count += 1  # Increase the vehicle's ride count
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

car1 = RoadVehicle(
    car_chassis["C1"],
    car_batteries["P1"],
    car_chargers["G1"],
    car_motors["M1"],
    car_autonomy["A3"],
)

car2 = RoadVehicle(
    car_chassis["C2"],
    car_batteries["P1"],
    car_chargers["G1"],
    car_motors["M2"],
    car_autonomy["A3"],
)


fleets: list[Fleet] = []
fleets.append(Fleet([car1], [15]))
fleets.append(Fleet([car1, car2], [10, 5]))

# TODO: Programmatically build fleets

results: list[Result] = []
for fleet in fleets:
    results.append(run_sim(fleet))

r = run_sim(fleet)

print(f"{len(r.vehicles)} fleet vehicles")
print()
print(f"Total Requests: {r.total_requests}")
print(f"Completed Rides: {r.completed}")
print(f"Dropped Rides: {r.dropped}")
print(f"Impossible Rides: {r.impossible}")
print()
print(f"Passenger Volume: {r.pax_volume}")
print(f"Average Wait: {r.average_wait} min")
print(f"Max Wait: {r.max_wait} min")
print()
print(f"Average Trip Distance: {r.average_distance} km")
print(f"Average Trip Duration: {r.average_duration} min")
print()
print(f"Availability: {r.availability}")
print(f"Utility: {r.utility}")
