from typing import Callable
from traffic_sim.strategies.baseline import ConstantController
from traffic_sim.strategies.idle_switch import IdleController
from traffic_sim.entities.controller import Controller
from traffic_sim.utils import print_padding, timer, quadratic_frustration_fn, FRUSTRATION_MAP
from traffic_sim.plotter import plot_frustrations, plot_hist_active
import concurrent.futures
import matplotlib.pyplot as plt
import yaml
from pathlib import Path


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

    return {'frustrations': frustrations, 'controllers': controllers}


if __name__ == '__main__':

    p = Path(__file__).with_name('config.yaml')
    with p.open('r') as f:
        config = yaml.safe_load(f)['simulation']

    sim_kwargs = config['shared']
    sim_kwargs['frustration_fn'] = FRUSTRATION_MAP[sim_kwargs['frustration_fn']]

    model_outputs = {}
    for model_name, model_kwargs in config['models'].items():
        model_kwargs['controller'] = globals()[model_kwargs['controller']]
        model_outputs[model_name] = main(**model_kwargs, **sim_kwargs)

    plot_frustrations(model_outputs)
    plot_hist_active(model_outputs, plot_total=True)
    plt.show()
