from abc import ABC, abstractmethod
from traffic_sim.entities.lane import Lane
from traffic_sim.utils import Clock
from traffic_sim.entities.car import Car
from random import randint
from typing import Self
import numpy as np


class Controller(ABC):

    def __init__(
            self,
            n_lanes: int,
            exit_rate: int,
            save_hist: bool = False,
    ):
        self.clock = Clock()
        self.exit_rate = exit_rate

        self.n_lanes = n_lanes
        self.lanes = [Lane(clock=self.clock) for _ in range(n_lanes)]

        self.active_lane_num = 0
        self.active_lane = self.lanes[self.active_lane_num]
        self.t = 0

        self.run_next_lane()

        self.save_hist = save_hist
        self.state_hist = {
            'lane_activity': {i: [] for i in range(self.n_lanes)},
            'active_light': []
        }

    @property
    def num_pending(self) -> int:
        return sum(lane.num_pending_cars for lane in self.lanes)

    @property
    def num_active(self) -> int:
        return sum(lane.num_active_cars for lane in self.lanes)

    @property
    def num_passed(self) -> int:
        return sum(lane.num_passed_cars for lane in self.lanes)

    @property
    def active_frustration(self) -> float:
        return sum(lane.active_frustration for lane in self.lanes)

    @property
    def passed_frustration(self) -> float:
        return sum(lane.passed_frustration for lane in self.lanes)

    @property
    def total_frustration(self) -> float:
        return self.active_frustration + self.passed_frustration

    def run_next_lane(self) -> Lane:
        self.active_lane.set_red()
        self.active_lane_num = (self.active_lane_num + 1) % self.n_lanes
        self.active_lane = self.lanes[self.active_lane_num]
        self.active_lane.set_green()
        return self.active_lane

    def populate_traffic_lights(
            self,
            num_cars: int,
            arrival_rate_min: float,
            **car_args
    ) -> Self:
        tx = 0
        for _ in range(num_cars):
            tx_arrival = int(np.random.exponential(60 / arrival_rate_min))
            tx += tx_arrival

            lane_num = randint(0, self.n_lanes - 1)
            car = Car(arrival_time=tx, clock=self.clock, **car_args)
            self.lanes[lane_num].add_pending(car)

        return self

    def run_iter(self) -> None:

        self.clock.tick()

        if self.num_pending == 0 and self.num_active == 0:
            return

        self.active_lane.update_pending_to_active()

        if self.clock.time - self.active_lane.last_exit_time > 1 / self.exit_rate:
            self.active_lane.drive_car()

        if self.is_time_up():
            self.run_next_lane()

        if self.save_hist:
            self.update_hist()

    @abstractmethod
    def is_time_up(self) -> bool:
        raise NotImplementedError('Must create a subclass and implement is_time_up method containing the AI.')

    def update_hist(self):
        for i in range(self.n_lanes):
            self.state_hist['lane_activity'][i].append(self.lanes[i].num_active_cars)
            self.state_hist['active_light'].append(self.active_lane_num)
