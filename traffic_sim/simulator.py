from traffic_sim.strategies import *
from typing import Callable
from traffic_sim.entities.controller import Controller
from traffic_sim.utils import print_padding, timer, FRUSTRATION_MAP, traffic_rate
from traffic_sim.plotter import plot_frustrations, plot_hist_active, plot_rate_estimate
import concurrent.futures
import matplotlib.pyplot as plt
from pathlib import Path
import yaml
from functools import partial


def sim(
    controller: Callable,
    lanes_config: list[dict],
    exit_rate: float = 0.5,
    frustration_fn: Callable = lambda x: x**2,
    verbose=False,
    save_hist=False,
    duration_hours: float = 24,
    **strategy_kwargs
) -> Controller:

    c = controller(
        lanes_config=lanes_config,
        exit_rate=exit_rate,
        save_hist=save_hist,
        frustration_fn=frustration_fn,
        **strategy_kwargs
    )

    while c.clock.time / 60 / 60 < duration_hours:
        c.run_iter()
        if verbose:
            print(f'-----Time = {c.clock.time}-----')
            print_padding(c.clock.time, pad_char='-', string_len=50)
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
    lanes_config: list[dict],
    exit_rate: float = 0.5,
    frustration_fn: Callable = lambda x: x ** 2,
    verbose=False,
    save_hist=False,
    **strategy_kwargs
):

    sim_kwargs = dict(
        controller=controller,
        lanes_config=lanes_config,
        exit_rate=exit_rate,
        frustration_fn=frustration_fn,
        verbose=verbose,
        save_hist=save_hist,
        **strategy_kwargs
    )

    print(f'Running simulations ({controller.__name__})...', end='')
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
    sim_kwargs['lanes_config'] = [
        {'traffic_rate_fn': partial(traffic_rate, **params)}
        for params in sim_kwargs['lanes_config']
    ]

    model_outputs = {}
    for model_name, model_kwargs in config['models'].items():
        model_kwargs['controller'] = globals()[model_kwargs['controller']]
        model_outputs[model_name] = main(**model_kwargs, **sim_kwargs)

    if config.get('n_sim', 1) > 20:
        plot_frustrations(model_outputs)

    plot_hist_active(model_outputs, plot_total=False)
    for v in model_outputs.values():
        plot_rate_estimate(v['controllers'][0])
    plt.show()
