from vehicle import *

####################
# Car Design Options
####################
car_chassis = {
    "C1": Chassis("C1", 2, 1350, 12 * 1000, 140),
    "C2": Chassis("C2", 4, 1600, 17 * 1000, 135),
    "C3": Chassis("C3", 6, 1800, 21 * 1000, 145),
    "C4": Chassis("C4", 8, 2000, 29 * 1000, 150),
    # "C5": Chassis("C5", 10, 2200, 31 * 1000, 160),
    # "C6": Chassis("C6", 16, 2500, 33 * 1000, 165),
    # "C7": Chassis("C7", 20, 4000, 38 * 1000, 180),
    # "C8": Chassis("C8", 30, 7000, 47 * 1000, 210),
}

car_batteries = {
    "P1": Battery("P1", 50, 6, 110),
    "P2": Battery("P2", 100, 11, 220),
    "P3": Battery("P3", 150, 15, 340),
    "P4": Battery("P4", 190, 19, 450),
    # "P5": Battery("P5", 250, 25, 570),
    # "P6": Battery("P6", 310, 30, 680),
    # "P7": Battery("P7", 600, 57, 1400),
}

car_chargers = {
    "G1": Charger("G1", 10, 1 * 1000, 1),
    "G2": Charger("G2", 20, 2.5 * 1000, 1.8),
    "G3": Charger("G3", 60, 7 * 1000, 5),
}

car_motors = {
    "M1": Motor("M1", 35, 50, 4200),
    "M2": Motor("M2", 80, 100, 9800),
    "M3": Motor("M3", 110, 210, 13650),
    "M4": Motor("M4", 200, 350, 20600),
}

car_autonomy = {
    "A3": Autonomy("A3", "3", 30, 1.5, 15 * 1000),
    # "A4": Autonomy("A4", "4", 60, 2.5, 35 * 1000),
    # "A5": Autonomy("A5", "5", 120, 5, 60 * 1000),
}

#####################
# Bike Design Options
#####################
bike_frames = {
    "B1": Chassis("B1", 1, 20, 2 * 1000, 30),
    "B2": Chassis("B2", 1, 17, 3 * 1000, 25),
    "B3": Chassis("B3", 2, 35, 3.5 * 1000, 40),
}

bike_batteries = {
    "E1": Battery("E1", 0.5, 0.6 * 1000, 5),
    "E2": Battery("E2", 1.5, 1.5 * 1000, 11),
    "E3": Battery("E3", 3, 2.6 * 1000, 17),
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


def car_design(configuration):
    """Return a RoadVehicle given a configuration string."""
    design = [configuration[i : i + 2] for i in range(0, len(configuration), 2)]
    return RoadVehicle(
        car_chassis[design[0]],
        car_batteries[design[1]],
        car_chargers[design[2]],
        car_motors[design[3]],
        car_autonomy[design[4]],
    )


def bike_design(configuration):
    """Return a Bicycle given a configuration string."""
    design = [configuration[i : i + 2] for i in range(0, len(configuration), 2)]
    return Bicycle(
        bike_frames[design[0]],
        bike_batteries[design[1]],
        bike_chargers[design[2]],
        bike_motors[design[3]],
    )
