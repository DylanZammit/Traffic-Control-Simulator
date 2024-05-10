from traffic_sim.simulator import sim
from traffic_sim.utils import quadratic_frustration_fn
from traffic_sim.strategies.baseline import ConstantController
from traffic_sim.strategies.idle_switch import IdleController
import matplotlib.pyplot as plt


if __name__ == '__main__':

    sim_kwargs = dict(
        controller=IdleController,
        # controller=ConstantController,
        n_lanes=3,
        exit_rate=0.5,
        arrival_rate_min=30,
        num_cars=1000,
        frustration_fn=quadratic_frustration_fn,
        wait_time=20,
        idle_time=20,
        verbose=False,
        save_hist=True,
    )

    c = sim(**sim_kwargs)

    for lane, num_active in c.state_hist['lane_activity'].items():
        dom = [i / 60 for i in range(len(num_active))]
        plt.plot(dom, num_active, label=f'Lane {lane+1}')

    plt.title('Num Active cars after 10 minutes')
    plt.xlabel('Time passed in minutes')
    plt.ylabel('Num cars waiting')
    plt.grid()
    plt.legend()
    plt.show()
