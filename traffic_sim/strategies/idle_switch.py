from traffic_sim.entities.controller import Controller


class IdleController(Controller):

    def __init__(self, wait_time: int, idle_time: int, **kwargs):
        super().__init__(**kwargs)
        self.wait_time = wait_time
        self.idle_time = idle_time

    def is_time_up(self) -> bool:
        is_lane_empty = self.active_lane.num_active_cars == 0
        is_idle_long = self.clock.diff(self.active_lane.last_exit_time) > self.idle_time
        is_max_time_elapsed = self.clock.diff(self.active_lane.active_since) > self.wait_time
        return is_lane_empty and is_idle_long or is_max_time_elapsed
