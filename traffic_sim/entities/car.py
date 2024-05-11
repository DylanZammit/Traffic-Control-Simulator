from typing import Callable
from traffic_sim.utils import Clock


class Car:

    def __init__(
            self,
            frustration_fn: Callable,
            clock: Clock
    ):
        """
        :param frustration_fn: patience penalty based on wait time: x ** 2, e ^ x - 1
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
        return f'Arrived at {self.arrival_time}'
