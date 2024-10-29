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

    def design(self):
        """Return a string describing the design vector."""
        pass

    def cost(self):
        """Return the cost of all the components [$]."""
        return (
            self.chassis.cost
            + self.battery.cost
            + self.charger.cost
            + self.motor.cost
            + self.autonomy.cost
        )

    def empty_weight(self):
        """Return the empty vehicle weight [kg]."""
        return (
            self.chassis.weight
            + self.battery.weight
            + self.charger.weight
            + self.motor.weight
            + self.autonomy.weight
        )

    def total_weight(self):
        """Return the vehicle weight with passengers [kg]."""
        load_factor = 0.75
        passenger_weight = 100  # kg
        return self.empty_weight() + (self.chassis.pax * load_factor * passenger_weight)

    def charge_time(self):
        """Return the charge time [hr]."""
        return self.battery.capacity / self.charger.power

    def power_consumption(self):
        """Return the power consumption [Wh/km]."""

        return (
            self.chassis.power
            + 0.1 * (self.total_weight() - self.chassis.weight)
            + self.autonomy.power
        )

    def range(self):
        """Return the range [km]."""
        return (self.battery.capacity * 1000) / self.power_consumption()

    def speed(self):
        """Return the speed [km/hr]."""
        pass

    def up_time(self):
        """Return uptime [hr]."""
        return self.range() / self.speed()

    def down_time(self):
        """Return downtime [hr]."""
        return self.charge_time() + 0.25

    def availability(self):
        """Return availability [%]."""
        return self.up_time() / (self.up_time() + self.down_time())

    def trip_throughput(self, distance):
        """Return the rate of trips [trip/hr]."""
        dwell_time = 1 / 60  # hr
        trip_time = (distance * 2) / self.speed() + (2 * dwell_time)
        return (1 / trip_time) * self.availability()

    def pax_throughput(self, distance):
        """Return maximum throughput [pax/hr] given an average one-way trip distance."""
        load_factor = 0.75
        return self.trip_throughput(distance) * self.chassis.pax * load_factor


class RoadVehicle(_Vehicle):

    def __init__(self, c: Chassis, b: Battery, chrg: Charger, m: Motor, a: Autonomy):

        # Battery may not exceed more than 1/3 of the chassis
        if b.weight > c.weight / 3:
            raise ValueError(
                f"Battery weight ({b.weight}) cannot exceed 1/3 chassis weight ({c.weight})."
            )

        super().__init__(c, b, chrg, m, a)

    def speed(self):
        """Return the speed [km/hr]."""
        # speed is capped at 40 kph (~25 mph)
        return min(700 * self.motor.power / self.total_weight(), 40)

    def design(self):
        """Return a string describing the design vector."""
        return f"{self.chassis.label}, {self.battery.label}, {self.charger.label}, {self.motor.label}, {self.autonomy.label}"


class Bicycle(_Vehicle):

    def __init__(self, c: Chassis, b: Battery, chrg: Charger, m: Motor):

        # Battery may not exceed more than 1/2 of the chassis
        if b.weight > c.weight / 2:
            raise ValueError(
                f"Battery weight ({b.weight}) cannot exceed 1/2 chassis weight ({c.weight})."
            )

        # A bicycle has level 4 autonomy included
        super().__init__(c, b, chrg, m, Autonomy("default", "4", 0, 0, 0))

    def speed(self):
        """Return the speed [km/hr]."""
        # speed is capped at 15 kph (~10 mph)
        return min(700 * self.motor.power / self.total_weight(), 15)

    def design(self):
        """Return a string describing the design vector."""
        return f"{self.chassis.label}, {self.battery.label}, {self.charger.label}, {self.motor.label}"


@dataclass
class Fleet:
    vehicles: list[_Vehicle]
    quantities: list[int]

    def cost(self):
        """Sum of vehicle cost [$]."""
        return sum([v.cost() * q for v, q in zip(self.vehicles, self.quantities)])

    def availability(self):
        """Overall system availability is the weighted average of vehicle availability [%]."""
        # Maximum of all vehicle availability
        # return max([v.availability() for v in self.vehicles])

        # Weighted average
        return sum(
            [
                v.availability() * (q / sum(self.quantities))
                for v, q in zip(self.vehicles, self.quantities)
            ]
        )

    def trip_throughput(self, distance):
        """Maximum sustained trip throughput of the fleet [trips/hr]."""
        return sum(
            [
                v.trip_throughput(distance) * q
                for v, q in zip(self.vehicles, self.quantities)
            ]
        )

    def pax_throughput(self, distance):
        """Maximum sustained passenger throughput [pax/hr]."""
        return sum(
            [
                v.pax_throughput(distance) * q
                for v, q in zip(self.vehicles, self.quantities)
            ]
        )

    def wait_time(self, distance):
        """Approximate wait time as the average headway / 2 [min]"""
        headways = [60 / v.trip_throughput(distance) for v in self.vehicles]
        weights = [q / sum(self.quantities) for q in self.quantities]
        return sum([(h / 2) * w for h, w in zip(headways, weights)])
        # return min([60 / v.trip_throughput(distance) for v in self.vehicles]) / 2
