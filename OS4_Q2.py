# Robaire Galliath
# EM 411, Fall 2024

# So we have a fleet of vehicles
# Road Vehicles (Cars) and Bikes
# Consider architectures using combinations of vehicles
# Evaluate different fleets composed of different vehicle designs

# Report:
# - vehicle speed and range
# - fleet throughput (pax / hr??)
# - average wait time
# - availability

# Calculate performance of the fleet against requirements

# Outputs from the model
# Passenger Volume (trips / day) (utility function)
# Peak Throughput (trips / hr) (utility function)
# Off-peak throughput (trips / hr)
# max wait (5 min) (utility function)
# max transport time (7 min)
# max transport outside (20 min)


# Ultimate goal, minimize cost while achieving L0 functionality
# (And also maximizing utility???)

from vehicle import *
from mvu import MVU, Utility
from dataclasses import dataclass

# Single Variate Utility Functions
volume = Utility([0, 500, 1000, 1500, 2000], [0, 0.2, 0.4, 0.8, 1.0])
throughput = Utility([0, 50, 100, 150, 200], [0, 0.2, 0.5, 0.9, 1.0])
wait_time = Utility([0, 5, 10, 15, 20, 30], [1.0, 0.95, 0.75, 0.4, 0.2, 0])
availability = Utility([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
utilities = [volume, throughput, wait_time, availability]
weights = [0.15, 0.25, 0.35, 0.25]  # Weights
mvu = MVU(utilities, weights)

batteries = {
    "P1": Battery("P1", 50, 6, 110),
    "P2": Battery("P2", 100, 11, 220),
    "P3": Battery("P3", 150, 15, 340),
    "P4": Battery("P4", 190, 19, 450),
    "P5": Battery("P5", 250, 25, 570),
    "P6": Battery("P6", 310, 30, 680),
    "P7": Battery("P7", 600, 57, 1400),
}

chassis = {
    "C1": Chassis("C1", 2, 1350, 12 * 1000, 140),
    "C2": Chassis("C2", 4, 1600, 17 * 1000, 135),
    "C3": Chassis("C3", 6, 1800, 21 * 1000, 145),
    "C4": Chassis("C4", 8, 2000, 29 * 1000, 150),
    "C5": Chassis("C5", 10, 2200, 31 * 1000, 160),
    "C6": Chassis("C6", 16, 2500, 33 * 1000, 165),
    "C7": Chassis("C7", 20, 4000, 38 * 1000, 180),
    "C8": Chassis("C8", 30, 7000, 47 * 1000, 210),
}

chargers = {
    "G1": Charger("G1", 10, 1 * 1000, 1),
    "G2": Charger("G2", 20, 2.5 * 1000, 1.8),
    "G3": Charger("G3", 60, 7 * 1000, 5),
}

motors = {
    "M1": Motor("M1", 35, 50, 4200),
    "M2": Motor("M2", 80, 100, 9800),
    "M3": Motor("M3", 110, 210, 13650),
    "M4": Motor("M4", 200, 350, 20600),
}

autonomy = {
    "A3": Autonomy("A3", "3", 30, 1.5, 15 * 1000),
    "A4": Autonomy("A4", "4", 60, 2.5, 35 * 1000),
    "A5": Autonomy("A5", "5", 120, 5, 60 * 1000),
}

d = 1.5  # average trip distance [km]

car1 = RoadVehicle(
    chassis["C1"], batteries["P1"], chargers["G1"], motors["M1"], autonomy["A3"]
)

car2 = RoadVehicle(
    chassis["C1"], batteries["P3"], chargers["G2"], motors["M4"], autonomy["A3"]
)

print(car1.availability())
print(car1.trip_throughput(d))
print(car1.pax_throughput(d))
print(car1.cost())
print()

fleet1 = Fleet([car1], [10])
print(fleet1.availability())
print(fleet1.trip_throughput(d))
print(fleet1.pax_throughput(d))
print(fleet1.cost())
print(fleet1.wait_time(d))
print()

fleet2 = Fleet([car1, car2], [8, 2])
print(fleet2.availability())
print(fleet2.trip_throughput(d))
print(fleet2.pax_throughput(d))
print(fleet2.cost())
print(fleet2.wait_time(d))


def utility_vec(fleet: Fleet, distance):
    """Return the utility vector for a fleet."""
    return [
        fleet.trip_throughput(distance) * 24,
        fleet.trip_throughput(distance),
        fleet.wait_time(distance),
        fleet.availability(),
    ]


print(f"Utility: {mvu.evaluate(utility_vec(fleet1, d))}")
print(f"Cost: {fleet1.cost()}")

# For a simple initial model we will assume the following
# All trips originate at Kendall/MIT with the demand given
# Trips have an average distance of 1 mile, with std-dev: 0.3 miles
# (1.5km, 0.4km stddev)
# Trips have 1 passenger
# Speed limit on surface streets is 25 mph (40 kph)
# Assume bikes have a speed of 10 mph (15 kph)
# Vehicles need to return to Kendall/MIT after dropping off their passenger(s)
# Vehicles will charge if they have less than 2 km range
# Vehicles will charge until they are full

# Essentially I see two approaches to developing a system model
# Approach 1
#   Back-calculate system performance given fleet design
#   From an implementation perspective this will probably make changing scenarios tricky
#
# Approach 2
#   Conduct a stochastic simulation of the fleet performance
#   Issue is this is sensitive to RNG so probably needs to be done a couple of times and averaged
#   My intuition is that scenarios would be easier to change