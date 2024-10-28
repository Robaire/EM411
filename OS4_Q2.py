# Robaire Galliath
# EM 411, Fall 2024

# So we have a fleet of vehicles
# Road Vehicles (Cars) and Bikes
# Consider architectures using combinations of vehicles
# Evaluate different fleets composed of different vehicle designs

# Report:
# - vehicle speed and range
# - fleet throughput (trips / hr)
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
import itertools
import matplotlib.pyplot as plt

# Single Variate Utility Functions
volume = Utility([0, 500, 1000, 1500, 2000], [0, 0.2, 0.4, 0.8, 1.0])
throughput = Utility([0, 50, 100, 150, 200], [0, 0.2, 0.5, 0.9, 1.0])
wait_time = Utility([0, 5, 10, 15, 20, 30], [1.0, 0.95, 0.75, 0.4, 0.2, 0])
availability = Utility([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
utilities = [volume, throughput, wait_time, availability]
weights = [0.15, 0.25, 0.35, 0.25]  # Weights
mvu = MVU(utilities, weights)

# Road Vehicle Design Options
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

# Bike Design Options
bike_batteries = {
    "E1": Battery("E1", 0.5, 0.6 * 1000, 5),
    "E2": Battery("E2", 1.5, 1.5 * 1000, 11),
    "E3": Battery("E3", 3, 2.6 * 1000, 17),
}

bike_frames = {
    "B1": Chassis("B1", 1, 20, 2 * 1000, 30),
    "B2": Chassis("B2", 1, 17, 3 * 1000, 25),
    "B3": Chassis("B3", 2, 35, 3.5 * 1000, 40),
}

bike_chargers = {
    "G1": Charger("G1", 0.2, 0.3 * 1000, 0.5),
    "G2": Charger("G2", 0.6, 0.5 * 1000, 1.2),
}

bike_motors = {
    "K1": Motor("K1", 5, 0.35, 300),
    "K2": Motor("K2", 4, 0.5, 400),
    "K3": Motor("K3", 7, 1.5, 600),
}


d = 1.5  # average trip distance [km]

"""
car1 = RoadVehicle(
    chassis["C1"], batteries["P1"], chargers["G1"], motors["M1"], autonomy["A3"]
)

car2 = RoadVehicle(
    chassis["C1"], batteries["P3"], chargers["G2"], motors["M4"], autonomy["A3"]
)
"""

"""
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
"""


# Create every possible car
cars: list[RoadVehicle] = []
for c in itertools.product(
    chassis.values(),
    batteries.values(),
    chargers.values(),
    motors.values(),
    autonomy.values(),
):
    try:
        cars.append(RoadVehicle(c[0], c[1], c[2], c[3], c[4]))
    except ValueError:
        continue

print(f"Cars: {len(cars)}")

bikes: list[Bicycle] = []
for b in itertools.product(
    bike_frames.values(),
    bike_batteries.values(),
    bike_chargers.values(),
    bike_motors.values(),
):
    try:
        bikes.append(Bicycle(b[0], b[1], b[2], b[3]))
    except ValueError:
        continue

print(f"Bikes: {len(bikes)}")


def utility_vec(fleet: Fleet, distance):
    """Return the utility vector for a fleet."""
    return [
        fleet.trip_throughput(distance) * 24,
        fleet.trip_throughput(distance),
        fleet.wait_time(distance),
        fleet.availability(),
    ]


# Consider the following cases
# fleets of 5, 10, 15, and 20 vehicles of one type
fleet_cars = [Fleet([v], [q]) for v, q in itertools.product(cars, [5, 10, 15, 20, 50])]
fleet_bikes = [
    Fleet([v], [q])
    for v, q in itertools.product(bikes, [20, 30, 40, 50, 100, 200, 300])
]

"""
fig, ax = plt.subplots()
ax.scatter(
    [f.cost() for f in fleet_cars],
    [mvu.evaluate(utility_vec(f, d)) for f in fleet_cars],
    c=[f.quantities[0] for f in fleet_cars],
    marker=".",
)
ax.scatter(
    [f.cost() for f in fleet_bikes],
    [mvu.evaluate(utility_vec(f, d)) for f in fleet_bikes],
    c=[f.quantities[0] for f in fleet_bikes],
    marker="^",
)
plt.show()
"""

# Filter results to those that meet L0 requirements
fleet_acceptable: list[Fleet] = []
for f in fleet_cars + fleet_bikes:
    (volume, throughput, wait_time, availability) = utility_vec(f, d)

    if volume > 1500 and throughput > 150 and wait_time < 5:
        fleet_acceptable.append(f)

print(f"Fleets that meet L0 requirements: {len(fleet_acceptable)}")

fig, ax = plt.subplots()
ax.scatter(
    [f.cost() for f in fleet_acceptable],
    [mvu.evaluate(utility_vec(f, d)) for f in fleet_acceptable],
    c=[f.quantities[0] for f in fleet_acceptable],
    marker=".",
)
plt.show()

# Filter results to the pareto front
fleet_pareto: list[Fleet] = []
for i, f1 in enumerate(fleet_acceptable):
    print(i)

    # For each element against every other element
    is_pareto = True
    for f2 in fleet_acceptable:
        if f1 == f2:
            continue

        # Compare performance
        u1 = mvu.evaluate(utility_vec(f1, d))
        c1 = f1.cost()

        u2 = mvu.evaluate(utility_vec(f2, d))
        c2 = f2.cost()

        # Does f2 have higher utility at lower cost?
        if u2 >= u1 and c2 <= c1:
            is_pareto = False
            break

    if is_pareto:
        fleet_pareto.append(f1)

print(f"Pareto Front: {len(fleet_pareto)}")
for f in fleet_pareto:
    (v, t, w, a) = utility_vec(f, d)
    print(f"Fleet Performance: {v}, {t}, {w}, {a}")
    print(f"Fleet Cost: {f.cost()}")
    print("Fleet Configuration:")
    for v, q in zip(f.vehicles, f.quantities):
        print(f"\t{q} | {v.design()}")
    print()


fig, ax = plt.subplots()
ax.set_xlabel("Cost [$]")
ax.set_ylabel("Utility [1]")
ax.set_title("Pareto Front")
ax.scatter(
    [f.cost() for f in fleet_pareto],
    [mvu.evaluate(utility_vec(f, d)) for f in fleet_pareto],
    c=[f.quantities[0] for f in fleet_pareto],
    marker="*",
)
ax.scatter(
    [f.cost() for f in fleet_acceptable],
    [mvu.evaluate(utility_vec(f, d)) for f in fleet_acceptable],
    c=[f.quantities[0] for f in fleet_acceptable],
    marker=".",
)
plt.show()


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
