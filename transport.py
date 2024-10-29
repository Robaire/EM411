# Robaire Galliath


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
    next_available: float  # The time this vehicle becomes available [hr]
    battery_capacity: float  # Current battery charge [kWh]

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.next_available = 0
        self.battery_capacity = self.vehicle.battery.capacity

    def range(self):
        """Current range [km]."""
        return (self.battery_capacity * 1000) / self.vehicle.power_consumption()

    def move(self, distance):
        """Decrease the battery capacity for a distance [km]."""
        self.battery_capacity -= (v.vehicle.power_consumption() * distance) / 1000
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
    start_time: float
    filled_time: float = None
    complete_time: float = None


###############################################
# Stochastic Model of Transport System Demand #
###############################################

# System Scenario 1 #
# ----------------- #
# Assumptions:
#   - All trips originate at Kendall/MIT
#   - Trips have an average distance of 1.5 km, std-dev 0.4km
#   - Vehicles return to Kendall/MIT after dropping off passengers
#   - Trips have 1-4 passengers
#   - Speed limit on surface streets is 40 kph (~25 mph)
#   - Speed limit for bikes is 15 kph (~10 mph)


# Model Approach
# Assume a uniform distribution of ride requests over each hour
# Use a probability model to determine if a passenger requests a ride that time step
# Use a probability model to determine the parameters of the ride requested (# passengers, distance)


#######################
# Model Configuration #
#######################
random.seed(411)  # Seed the RNG

# Distance Model
distance = lambda: random.gauss(1.5, 0.4)  # 1.5 km average, 0.4 km std-dev
# distance = lambda: random.gauss(5, 2)  # 1.5 km average, 0.4 km std-dev
# Passenger Model
passengers = lambda: max(round(random.lognormvariate(0, 0.5)), 1)

# Demand over a 24 hour period, evenly spaced
DEMAND = [15, 5, 15, 50, 150, 150, 150, 100, 75, 100, 50, 35]

DWELL_TIME = 1 / 60  # [hr] (one minute)
CHARGE_DISTANCE = (
    5  # [km] The vehicle when charge with the range drops beneath this value
)
CHARGE_TIME_PENALTY = 0.25  # [hr] fixed time penalty for charging

####################
# Simulation Setup #
####################

rides: list[Ride] = []
for i, demand in enumerate(DEMAND):
    interval = 24 / len(DEMAND)

    for _ in range(math.ceil(demand)):
        time = random.uniform(i * interval, (i + 1) * interval)
        rides.append(Ride(distance(), passengers(), time))

# Sort rides by time
rides = sorted(rides, key=lambda x: x.start_time)

test_car = RoadVehicle(
    car_chassis["C1"],
    car_batteries["P1"],
    car_chargers["G1"],
    car_motors["M1"],
    car_autonomy["A3"],
)


###################
# Simulation Loop #
###################
vehicles: list[RealVehicle] = []
for _ in range(20):
    vehicles.append(RealVehicle(test_car))  # need to create new instances

for ride in rides:

    # Find the next available vehicle that meets the ride criteria
    vehicles = sorted(vehicles, key=lambda x: x.next_available)
    for v in vehicles:

        if ride.passengers <= v.vehicle.chassis.pax and v.range() >= ride.distance * 2:

            # Set the fill time for the ride
            ride.filled_time = max(ride.start_time, v.next_available)

            travel_time = (ride.distance / v.vehicle.speed()) + DWELL_TIME

            # Set the completed time for the ride
            ride.complete_time = ride.filled_time + travel_time

            # Set the next availability for the vehicle
            v.next_available = ride.filled_time + travel_time * 2

            # Adjust the battery capacity
            v.move(ride.distance * 2)

            # If the vehicle needs to charge afterwards, set the availability
            if v.range() <= CHARGE_DISTANCE:
                v.next_available += v.charge_time() + CHARGE_TIME_PENALTY

            break


# Print Summary
print(f"{len(rides)} ride requests")
print(f"{len(vehicles)} fleet vehicles")

completed_rides = [r for r in rides if r.complete_time]
print(f"{len(completed_rides)} rides completed")

wait_times = [
    (r.filled_time - r.start_time) * 60 for r in rides if r.filled_time
]  # [min]
print(f"Average Wait: {sum(wait_times) / len(wait_times)} minutes")

# Check for new requests this time step, add them to the queue
# Process any queued requests
#   Check all queued requests since some might be able to be filled
# Step the fleet vehicles forward in time
# Repeat

# Given a fleet configuration find a vehicle to fill the request
# Track state information of the vehicles throughout the simulation
# Log statistics of system behavior (such as each requests wait time, etc...)
# Report system performance
# Report fleet utility based on system performance