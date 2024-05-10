from collections import deque
import numpy as np
from traffic_sim.utils import Clock
from traffic_sim.entities.car import Car


class Lane:

    def __init__(self, clock: Clock):
        self.green = False
        self.clock = clock
        self.active_since = -np.inf
        self.last_active_time = -np.inf
        self.last_exit_time = -np.inf

        self.active: deque[Car] = deque()
        self.pending: deque[Car] = deque()
        self.passed: deque[Car] = deque()

    def set_green(self) -> None:
        self.green = True
        self.active_since = self.clock.time

    def set_red(self) -> None:
        self.green = False
        self.last_active_time = self.clock.time

    @property
    def num_active_cars(self) -> int:
        return len(self.active)

    @property
    def num_pending_cars(self) -> int:
        return len(self.pending)

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

    def add_pending(self, car: Car) -> None:
        self.pending.appendleft(car)

    def update_pending_to_active(self) -> None:
        if len(self.pending) == 0:
            return

        car = self.pending[-1]
        while self.clock.time > car.arrival_time and len(self.pending) > 0:
            car = self.pending[-1]
            self.active.append(self.pending.pop())

    def drive_car(self) -> None:
        if self.num_active_cars == 0:
            return

        exit_car = self.active.pop()
        exit_car.exit_time = self.clock.time
        self.passed.append(exit_car)
        self.last_exit_time = self.clock.time
