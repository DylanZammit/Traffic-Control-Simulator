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
        """
        Initializes the Controller object with the provided lanes configuration, exit rate, frustration function,
        and save history flag.

        Parameters
        ----------
        lanes_config : List[dict]
            A list of dictionaries representing the configuration of lanes.
        exit_rate : int
            The rate at which cars exit the lanes.
        frustration_fn : Callable
            A function that calculates the frustration level of cars in the lanes.
        save_hist : bool, optional
            A flag indicating whether to save the history of the controller's state.
            Defaults to False.
        """
        self.clock = Clock()
        self.exit_rate = exit_rate

        self.n_lanes = len(lanes_config)
        self.lanes = [
            Lane(clock=self.clock, frustration_fn=frustration_fn, **lane_config)
            for lane_config in lanes_config
        ]

        self.active_lane_num = -1
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
        """
        Sets the current active lane to red, increments the active lane number to the next lane in a circular manner,
        sets the new active lane to green, and returns the updated active lane.

        Returns:
        -------
        Lane: The updated active lane after the switch.
        """
        self.active_lane.set_red()
        self.active_lane_num = (self.active_lane_num + 1) % self.n_lanes
        self.active_lane = self.lanes[self.active_lane_num]
        self.active_lane.set_green()
        return self.active_lane

    def run_iter(self) -> None:
        """
        Updates the controller state for each iteration by ticking the clock,
        updating active lanes with new cars, driving cars if conditions are met,
        and triggering lane switches based on time and conditions.
        """
        self.clock.tick()

        for lane in self.lanes:
            lane.update_new_active()

        num_active_cars = self.active_lane.num_active_cars
        time_since_last_exit = self.clock.time - self.active_lane.last_exit_time

        if num_active_cars > 0 and time_since_last_exit >= (1 / self.exit_rate):
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
