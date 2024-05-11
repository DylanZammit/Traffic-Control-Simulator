from typing import Callable
from traffic_sim.strategies.baseline import ConstantController
from traffic_sim.strategies.idle_switch import IdleController
from traffic_sim.entities.controller import Controller
from traffic_sim.utils import print_padding, timer, quadratic_frustration_fn
from traffic_sim.plotter import plot_frustrations, plot_hist_active
import concurrent.futures
import matplotlib.pyplot as plt


def sim(
    controller: Callable,
    n_lanes: int = 3,
    exit_rate: float = 0.5,
    arrival_rate_min: float = 30,
    num_cars: int = 1000,
    frustration_fn: Callable = lambda x: x**2,
    verbose=False,
    save_hist=False,
    **strategy_kwargs
) -> Controller:

    c = controller(
        n_lanes=n_lanes,
        exit_rate=exit_rate,
        save_hist=save_hist,
        **strategy_kwargs
    )

    c.populate_traffic_lights(
        num_cars=num_cars,
        arrival_rate_min=arrival_rate_min,
        frustration_fn=frustration_fn,
    )

    while c.num_pending > 0 or c.num_active > 0:
        c.run_iter()
        if verbose:
            print(f'-----Time = {c.clock.time}-----')
            print_padding(c.clock.time, pad_char='-', string_len=50)
            print(f'Number Pending = {c.num_pending}')
            print(f'Number Pending = {c.num_active}')
            print(f'Number Pending = {c.num_passed}')

    if verbose:
        print('Total frustration = {:,}'.format(c.total_frustration))
        print('Average frustration = {:,.2f}'.format(c.total_frustration / c.num_passed))
        print('Total cars = {}'.format(c.num_passed))

    return c


def sim_pool(kwargs: dict) -> Controller:
    return sim(**kwargs)


@timer
def main(
    controller: Callable,
    n_sim: int,
    n_lanes: int = 3,
    exit_rate: float = 0.5,
    arrival_rate_min: float = 30,
    num_cars: int = 1000,
    frustration_fn: Callable = lambda x: x ** 2,
    verbose=False,
    save_hist=False,
    **strategy_kwargs
):

    sim_kwargs = dict(
        controller=controller,
        n_lanes=n_lanes,
        exit_rate=exit_rate,
        arrival_rate_min=arrival_rate_min,
        num_cars=num_cars,
        frustration_fn=frustration_fn,
        verbose=verbose,
        save_hist=save_hist,
        **strategy_kwargs
    )

    print('Running simulations...', end='')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        controllers = executor.map(sim_pool, [sim_kwargs] * n_sim)
    print('done')

    # I want to refer to these values again in the future
    controllers = list(controllers)
    frustrations = []
    for c in controllers:
        avg_frustration = c.total_frustration / c.num_passed
        frustrations.append(avg_frustration)

    return frustrations, controllers


if __name__ == '__main__':

    frust_fn = quadratic_frustration_fn
    # frust_fn = expon_frustration_fn

    sim_kwargs = dict(
        n_sim=1000,
        n_lanes=3,
        exit_rate=0.5,
        arrival_rate_min=20,
        num_cars=1000,
        frustration_fn=frust_fn,
        verbose=False,
        save_hist=True,
    )

    baseline_frustration, baseline_controllers = main(
        controller=ConstantController,
        wait_time=20,
        **sim_kwargs
    )

    baseline40_frustration, baseline40_controllers = main(
        controller=ConstantController,
        wait_time=40,
        **sim_kwargs
    )

    idle_frustration, idle_controllers = main(
        controller=IdleController,
        wait_time=20,
        idle_time=5,
        **sim_kwargs
    )

    idle40_frustration, idle40_controllers = main(
        controller=IdleController,
        wait_time=40,
        idle_time=5,
        **sim_kwargs
    )

    models_frustration = {
        'Baseline_20': baseline_frustration,
        'Baseline_40': baseline40_frustration,
        'Idle_20_5': idle_frustration,
        'Idle_40_5': idle40_frustration
    }

    plot_frustrations(models_frustration)
    plt.figure()
    plot_hist_active(baseline40_controllers[0], extra_title='Baseline 40s')
    plt.figure()
    plot_hist_active(idle40_controllers[0], extra_title='Idle 40s - 5s wait')
    plt.show()
