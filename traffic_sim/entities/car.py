from typing import Callable
from traffic_sim.utils import Clock


class Car:

    def __init__(
            self,
            frustration_fn: Callable,
            clock: Clock
    ):
        """
        Initializes a Car instance with the given frustration function and clock.

        Parameters:
        -----------
        self: Car
            The Car instance.
        frustration_fn: Callable
            The function that calculates the frustration of the car.
        clock: Clock
            The clock instance used to track time.

        Returns:
        --------
        None
        """
        self.clock = clock
        self.frustration_fn = frustration_fn

        self.arrival_time = self.clock.time
        self.exit_time = None

    @property
    def frustration(self) -> float:
        return self.frustration_fn(self.wait)

    @property
    def wait(self) -> int:
        return (self.exit_time if self.exit_time else self.clock.time) - self.arrival_time

    def __repr__(self) -> str:
        return f'Arrived from {self.arrival_time} to {self.exit_time}'
