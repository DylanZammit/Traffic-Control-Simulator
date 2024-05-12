from traffic_sim.entities.controller import Controller
import numpy as np
from scipy.optimize import minimize


class SnapshotController(Controller):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def queue_penalty(self, t: list[float]):
        return sum(max(0, (lane.entry_rate - self.exit_rate * 2 * ti * 60)) ** 2 for ti, lane in zip(t, self.lanes))

    def is_time_up(self) -> bool:
        x0 = np.array([1 / self.n_lanes] * self.n_lanes)
        bounds = [(0, 1) for _ in range(self.n_lanes)]
        cons = {'type': 'eq', 'fun': lambda x: sum(x) - 1}
        res = minimize(
            self.queue_penalty,
            x0=x0,
            bounds=bounds,
            constraints=cons,
        )
        wait_time = int(res.x[self.active_lane_num] * 60)
        is_max_time_elapsed = self.clock.diff(self.active_lane.active_since) > wait_time
        return is_max_time_elapsed
