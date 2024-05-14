from traffic_sim.entities.controller import Controller


class ConstantController(Controller):

    def __init__(self, wait_time: int, **kwargs):
        super().__init__(**kwargs)
        self.wait_time = wait_time

    def is_time_up(self) -> bool:
        """
        Check if the maximum time has elapsed since the lane became active.

        Returns
        -------
        bool
            True if the maximum time has elapsed, False otherwise.
        """
        is_max_time_elapsed = self.clock.diff(self.active_lane.active_since) > self.wait_time
        return is_max_time_elapsed
