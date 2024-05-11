from traffic_sim.entities.controller import Controller
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict


def plot_frustrations(models_frustration: Dict[str, list[float]]) -> None:

    min_val = min(min(q) for q in models_frustration.values())
    max_val = max(max(q) for q in models_frustration.values())

    bins = np.linspace(min_val, max_val, 20)

    for colour, (model_name, frustration) in zip(mcolors.TABLEAU_COLORS, models_frustration.items()):
        mean_frustration = float(np.mean(frustration))
        plt.hist(frustration, bins, density=True, alpha=0.3, color=colour)
        plt.axvline(x=mean_frustration, color=colour, label=model_name)

    subtitle = r'Histogram of frustration $f(x) = (\dfrac{x}{60})^2$ and average frustration.'
    plt.title(subtitle, fontsize=8)
    plt.suptitle('Frustration by Model')
    plt.legend()


def plot_hist_active(
        controller: Controller,
        extra_title: str = None,
        plot_total: bool = False,
):
    dom = [i / 60 for i in range(controller.clock.time)]
    for lane, num_active in controller.state_hist['lane_activity'].items():
        plt.plot(dom, num_active, label=f'Lane {lane+1}')

    if plot_total:
        hist = list(controller.state_hist['lane_activity'].values())
        total = [sum(x) for x in zip(*hist)]

        plt.plot(dom, total, label='Total', color='black')

    title = 'Num Active cars after 10 minutes'
    title = f'{title}: {extra_title}' if extra_title else title
    plt.title(title)
    plt.xlabel('Time passed in minutes')
    plt.ylabel('Num cars waiting')
    plt.grid()
    plt.legend()
