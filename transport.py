# Robaire Galliath
# EM 411, Fall 2024


from dataclasses import dataclass
from mvu import MVU, Utility
from vehicle import _Vehicle, Fleet

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

    def __init__(
        self,
        rides: list[Ride],
        vehicles: list[RealVehicle],
        fleet: Fleet,
        availability: float,
    ):
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

        wait_times = [r.wait_time() * 60 for r in completed]  # [min]
        self.average_wait = sum(wait_times) / len(wait_times)
        self.max_wait = max(wait_times)

        trip_times = [r.travel_time() * 60 for r in completed]
        self.average_duration = sum(trip_times) / len(trip_times)

        trip_dist = [r.distance for r in completed]
        self.average_distance = sum(trip_dist) / len(trip_dist)

        self.availability = len([w for w in wait_times if w < availability]) / len(
            rides
        )

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


@dataclass
class Simulation:

    max_wait: float  # [hr]
    availability: float  # [min]
    dwell_time: float  # [hr]
    charge_distance: float  # [km]
    charge_time_penalty: float  # [hr]

    def run(self, args):
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
                    if v.next_available - ride.start_time > self.max_wait:
                        # Drop the ride
                        ride.complete_time = -2
                        break

                    # One way travel time
                    travel_time = (ride.distance / v.vehicle.speed()) + self.dwell_time

                    # Update ride parameters
                    ride.filled_time = max(ride.start_time, v.next_available)
                    ride.complete_time = ride.filled_time + travel_time

                    # Update vehicle parameters
                    v.next_available = (
                        ride.filled_time + travel_time * 2
                    )  # Availability
                    v.move(ride.distance * 2)  # Update the battery charge
                    if v.range() <= self.charge_distance:
                        v.next_available += v.charge_time() + self.charge_time_penalty
                        v.battery_capacity = (
                            v.vehicle.battery.capacity
                        )  # Reset the battery
                    # Could make a decision to charge based on the availability of all other vehicles

                    break

        ###################
        # Analyze Results #
        ###################
        return Result(rides, vehicles, fleet, self.availability)
