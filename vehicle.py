# Robaire Galliath
# EM 411, Fall 2024

from dataclasses import dataclass


@dataclass
class Battery:
    label: str
    capacity: float  # kWh
    cost: float  # $
    weight: float  # kg


@dataclass
class Chassis:
    label: str
    pax: int
    weight: float  # kg
    cost: float  # $
    power: float  # Wh/km


@dataclass
class Charger:
    label: str
    power: float  # kW
    cost: float  # $
    weight: float  # kg


@dataclass
class Motor:
    label: str
    weight: float  # kg
    power: float  # kW
    cost: float  # $


@dataclass
class Autonomy:
    label: str
    level: str
    weight: float  # kg
    power: float  # Wh/km
    cost: float  # $


class _Vehicle:
    chassis: Chassis
    battery: Battery
    charger: Charger
    motor: Motor
    autonomy: Autonomy

    def __init__(self, c: Chassis, b: Battery, chrg: Charger, m: Motor, a: Autonomy):
        self.chassis = c
        self.battery = b
        self.charger = chrg
        self.motor = m
        self.autonomy = a

    def cost(self):
        return (
            self.chassis.cost
            + self.battery.cost
            + self.charger.cost
            + self.motor.cost
            + self.autonomy.cost
        )

    def empty_weight(self):
        return (
            self.chassis.weight
            + self.battery.weight
            + self.charger.weight
            + self.motor.weight
            + self.autonomy.weight
        )


class RoadVehicle(_Vehicle):

    def __init__(self, c: Chassis, b: Battery, chrg: Charger, m: Motor, a: Autonomy):

        # Battery may not exceed more than 1/3 of the chassis
        if b.weight > c.weight / 3:
            raise ValueError(
                f"Battery weight ({b.weight}) cannot exceed 1/3 chassis weight ({c.weight})."
            )

        super.__init__(c, b, chrg, m, a)


class Bicycle(_Vehicle):

    def __init__(self, c: Chassis, b: Battery, chrg: Charger, m: Motor):

        # Battery may not exceed more than 1/2 of the chassis
        if b.weight > c.weight / 2:
            raise ValueError(
                f"Battery weight ({b.weight}) cannot exceed 1/2 chassis weight ({c.weight})."
            )

        # A bicycle has level 4 autonomy included
        super.__init__(c, b, chrg, m, Autonomy("", "4", 0, 0, 0))
