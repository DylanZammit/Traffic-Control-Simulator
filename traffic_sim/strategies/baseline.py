from traffic_sim.controller import Controller


class ConstantController(Controller):

    def __init__(self, wait_time: int, **kwargs):
        super().__init__(**kwargs)
        self.wait_time = wait_time

    def is_time_up(self) -> bool:
        return self.clock.diff(self.active_lane.active_since) > self.wait_time
