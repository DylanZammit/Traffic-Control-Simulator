from traffic_sim.controller import Controller


class IdleController(Controller):

    def __init__(self, wait_time: int, idle_time: int, **kwargs):
        super().__init__(**kwargs)
        self.wait_time = wait_time
        self.idle_time = idle_time

    def is_time_up(self) -> bool:
        is_idle = self.active_lane.num_active_cars == 0 and \
                self.clock.diff(self.active_lane.last_exit_time) > self.idle_time
        return is_idle or self.clock.diff(self.active_lane.active_since) > self.wait_time
