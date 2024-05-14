from traffic_sim.entities.controller import Controller
from traffic_sim.entities.lane import Lane
import numpy as np
from scipy.optimize import minimize


class SnapshotController(Controller):

    def __init__(self, rate_lookback: int = 300, loop_duration: int = 60, **kwargs):
        super().__init__(**kwargs)
        self.rate_lookback = rate_lookback
        self.loop_duration = loop_duration

    def queue_penalty(self, t: list[float]):
        """
        Calculates the penalty based on the entry rate estimate, exit rate, and time durations.

        Parameters:
        -----------
        t: list[float]
            List of time proportions for each lane.

        Returns:
        --------
        float
            The calculated penalty based on the entry rate estimate, exit rate, and time durations squared.
        """
        return sum(max(0, (lane.entry_rate_estimate - self.exit_rate * ti * 60)) ** 2 for ti, lane in zip(t, self.lanes))

    def estimate_entry_rate(self, lane: Lane):
        """
        Calculates the estimated entry rate based on the number of cars that have arrived within the rate lookback period.

        Parameters:
        -----------
        self: SnapshotController
            The SnapshotController instance.
        lane: Lane
            The lane for which the entry rate is being estimated.

        Returns:
        --------
        float
            The estimated entry rate calculated based on the number of cars and the rate lookback time.
        """
        n_cars = next((
            i for i, car in enumerate(lane.active + lane.passed)
            if self.clock.diff(car.arrival_time) > self.rate_lookback
        ), len(lane.active) + len(lane.passed))
        return n_cars / self.rate_lookback * 60

    def is_time_up(self) -> bool:
        """
        Checks if the maximum time has elapsed for the current active lane based on
        the incoming rates of all 3 lanes and returns a boolean value.

        Parameters:
        -----------
        self: SnapshotController
            The SnapshotController instance.

        Returns:
        --------
        bool
            True if the maximum time has elapsed for the active lane, False otherwise.
        """
        is_first_lane = self.active_lane_num == 0
        is_loop_start = self.clock.diff(self.active_lane.active_since) == 1

        if is_first_lane and is_loop_start:
            for lane in self.lanes:
                lane.entry_rate_estimate = self.estimate_entry_rate(lane)

            x0 = np.array([1 / self.n_lanes] * self.n_lanes)
            bounds = [(0, 1) for _ in range(self.n_lanes)]
            cons = {'type': 'eq', 'fun': lambda x: sum(x) - 1}

            res = minimize(
                self.queue_penalty,
                x0=x0,
                bounds=bounds,
                constraints=cons,
            )

            for wait_time, lane in zip(res.x, self.lanes):
                lane.wait_time = int(wait_time * self.loop_duration)

        if self.save_hist:
            for i, lane in enumerate(self.lanes):
                key = f'lane_{i}_wait_time'
                val = lane.entry_rate_estimate
                # TODO: use default dict
                if key in self.state_hist:
                    self.state_hist[key].append(val)
                else:
                    self.state_hist[key] = [val]

        is_max_time_elapsed = self.clock.diff(self.active_lane.active_since) > self.active_lane.wait_time
        return is_max_time_elapsed
