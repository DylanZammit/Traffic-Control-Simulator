from collections import deque

import numpy as np
from traffic_sim.utils import Clock
from traffic_sim.entities.car import Car
from typing import Callable


class Lane:

    def __init__(self, clock: Clock, traffic_rate_fn: Callable, frustration_fn: Callable):
        self.clock = clock
        self.active_since = -np.inf
        self.last_active_time = -np.inf
        self.last_exit_time = -np.inf

        self.traffic_rate_fn = traffic_rate_fn

        self.active: deque[Car] = deque()
        self.passed: deque[Car] = deque()

        self.frustration_fn = frustration_fn

    def set_green(self) -> None:
        self.active_since = self.clock.time

    def set_red(self) -> None:
        self.last_active_time = self.clock.time

    @property
    def entry_rate(self) -> int:
        return self.traffic_rate_fn(self.clock.time / 60 / 60)

    @property
    def num_active_cars(self) -> int:
        return len(self.active)

    @property
    def num_passed_cars(self) -> int:
        return len(self.passed)

    @property
    def active_frustration(self) -> float:
        return sum(car.frustration for car in self.active)

    @property
    def active_waiting_time(self) -> float:
        return sum(car.wait for car in self.active)

    @property
    def passed_frustration(self) -> float:
        return sum(car.frustration for car in self.passed)

    @property
    def total_frustration(self) -> float:
        return self.active_frustration + self.passed_frustration

    def update_new_active(self) -> None:

        current_rate = self.traffic_rate_fn(self.clock.time / 60 / 60)

        num_new_cars = int(np.random.poisson(current_rate / 60))

        for _ in range(num_new_cars):
            car = Car(
                frustration_fn=self.frustration_fn,
                clock=self.clock,
            )
            self.active.appendleft(car)

    def drive_car(self) -> None:
        if self.num_active_cars == 0:
            return

        exit_car = self.active.pop()
        exit_car.exit_time = self.clock.time
        self.passed.appendleft(exit_car)
        self.last_exit_time = self.clock.time
