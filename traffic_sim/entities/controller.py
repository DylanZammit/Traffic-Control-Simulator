from abc import ABC, abstractmethod
from traffic_sim.entities.lane import Lane
from traffic_sim.utils import Clock
from typing import List, Callable


class Controller(ABC):

    def __init__(
            self,
            lanes_config: List[dict],
            exit_rate: int,
            frustration_fn: Callable,
            save_hist: bool = False,
    ):
        self.clock = Clock()
        self.exit_rate = exit_rate

        self.n_lanes = len(lanes_config)
        self.lanes = [
            Lane(clock=self.clock, frustration_fn=frustration_fn, **lane_config)
            for lane_config in lanes_config
        ]

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

    def run_iter(self) -> None:

        self.clock.tick()

        for lane in self.lanes:
            lane.update_new_active()

        num_active_cars = self.active_lane.num_active_cars
        time_since_last_exit = self.clock.time - self.active_lane.last_exit_time

        if num_active_cars > 0 and time_since_last_exit >= (1 / self.exit_rate):
            # two-lane road
            self.active_lane.drive_car()
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
