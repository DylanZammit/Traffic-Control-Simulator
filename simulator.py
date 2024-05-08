from typing import Callable
from traffic_sim.strategies.baseline import ConstantController
from traffic_sim.controller import Controller


def sim(
    n_lanes: int = 3,
    pop_lag: int = 4,
    arrival_rate_min: float = 30,
    num_cars: int = 1000,
    frustration_fn: Callable = lambda x: x**2,
    verbose=False,
) -> Controller:

    c = ConstantController(
        n_lanes=n_lanes,
        pop_lag=pop_lag,
        wait_time=20,
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
            print(f'Number Pending = {c.num_pending}')
            print(f'Number Pending = {c.num_active}')
            print(f'Number Pending = {c.num_passed}')

    if verbose:
        print('Total frustration = {:,}'.format(c.total_frustration))
        print('Average frustration = {:,.2f}'.format(c.total_frustration / c.num_passed))
        print('Total cars = {}'.format(c.num_passed))

    return c


def main(
    n_sim: int,
    n_lanes: int = 3,
    pop_lag: int = 4,
    arrival_rate_min: float = 30,
    num_cars: int = 1000,
    frustration_fn: Callable = lambda x: x ** 2,
    verbose=False,
):

    frustrations = []
    for i in range(1, n_sim+1):
        if i % 50 == 0:
            print(f'Sim {i}')
        c = sim(
            n_lanes=n_lanes,
            pop_lag=pop_lag,
            arrival_rate_min=arrival_rate_min,
            num_cars=num_cars,
            frustration_fn=frustration_fn,
            verbose=verbose,
        )
        avg_frustration = c.total_frustration / c.num_passed
        frustrations.append(avg_frustration)

    return frustrations


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    frustrations = main(
        n_sim=1000,
        n_lanes=3,
        pop_lag=4,
        arrival_rate_min=30,
        num_cars=1000,
        frustration_fn=lambda x: x ** 2,
        verbose=False,
    )

    plt.hist(frustrations, density=True, bins=20)
    plt.show()
