from traffic_sim.entities.controller import Controller
from traffic_sim.entities.lane import Lane
import numpy as np
from scipy.optimize import minimize


class SnapshotController(Controller):

    def __init__(self, rate_lookback: int = 300, **kwargs):
        super().__init__(**kwargs)
        self.rate_lookback = rate_lookback

        self.x0 = np.array([1 / self.n_lanes] * self.n_lanes)
        self.bounds = [(0, 1) for _ in range(self.n_lanes)]
        self.cons = {'type': 'eq', 'fun': lambda x: sum(x) - 1}

    def queue_penalty(self, t: list[float]):
        return sum(max(0, (lane.entry_rate_estimate - self.exit_rate * ti * 60)) ** 2 for ti, lane in zip(t, self.lanes))

    def estimate_entry_rate(self, lane: Lane):
        n_cars = next((
            i for i, car in enumerate(lane.active + lane.passed)
            if self.clock.diff(car.arrival_time) > self.rate_lookback
        ), len(lane.active) + len(lane.passed))
        return n_cars / self.rate_lookback * 60

    def is_time_up(self) -> bool:

        is_first_lane = self.active_lane_num == 0
        is_loop_start = self.clock.diff(self.active_lane.active_since) == 1

        if is_first_lane and is_loop_start:
            for lane in self.lanes:
                lane.entry_rate_estimate = self.estimate_entry_rate(lane)

            res = minimize(
                self.queue_penalty,
                x0=self.x0,
                bounds=self.bounds,
                constraints=self.cons,
            )

            for wait_time, lane in zip(res.x, self.lanes):
                lane.wait_time = int(wait_time * 60)

        if self.save_hist:
            for i, lane in enumerate(self.lanes):
                self.state_hist[f'lane_{i}_wait_time'] = lane.entry_rate_estimate

        is_max_time_elapsed = self.clock.diff(self.active_lane.active_since) > self.active_lane.wait_time
        return is_max_time_elapsed
