from traffic_sim.entities.controller import Controller
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


def plot_frustrations(models: dict) -> None:

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    models_frustration = {name: val['frustrations'] for name, val in models.items()}
    min_val = min(min(q) for q in models_frustration.values())
    max_val = max(max(q) for q in models_frustration.values())

    bins = np.linspace(min_val, max_val, 20)

    for colour, (model_name, frustration) in zip(mcolors.TABLEAU_COLORS, models_frustration.items()):
        mean_frustration = float(np.mean(frustration))
        ax.hist(frustration, bins, density=True, alpha=0.3, color=colour)
        ax.axvline(x=mean_frustration, color=colour, label=model_name)

    subtitle = r'Histogram of frustration $f(x) = (\dfrac{x}{60})^2$ and average frustration.'
    ax.set_title(subtitle, fontsize=8)
    ax.legend()
    fig.suptitle('Frustration by Model')


def plot_hist_active(
        models: dict,
        plot_total: bool = False,
        idx: int = 0,
):

    num_models = len(models)

    grid_map = {
        1: (1, 1),
        2: (2, 1),
        3: (3, 1),
        4: (4, 1),
        5: (3, 2),
        6: (3, 2),
        7: (4, 2),
        8: (4, 2),
    }

    grid = grid_map.get(num_models, (num_models, 1))
    fig, ax = plt.subplots(*grid, sharex=True)
    if not isinstance(ax, np.ndarray):
        ax = np.array([ax])

    for ax_i, (model_name, model_metadata) in zip(ax.flatten(), models.items()):
        controller = model_metadata['controllers'][idx]
        avg_frustration = model_metadata['frustrations'][idx]
        dom = np.array([i for i in range(controller.clock.time)])

        time_unit = 'seconds'
        if 120 <= len(dom) < 7200:
            time_unit = 'minutes'
            dom = dom / 60
        elif len(dom) >= 7200:
            time_unit = 'hours'
            dom = dom / (60 * 60)

        for lane, num_active in controller.state_hist['lane_activity'].items():
            ax_i.plot(dom, num_active, label=f'Lane {lane+1}')

        if plot_total:
            hist = list(controller.state_hist['lane_activity'].values())
            total = [sum(x) for x in zip(*hist)]

            ax_i.plot(dom, total, label='Total', color='black')

        title = f'{model_name} frustration: {avg_frustration:.2f}'
        ax_i.set_title(title)
        ax_i.set_xlabel(f'Time passed in {time_unit}')
        ax_i.set_ylabel('Num cars waiting')
        ax_i.grid()
        ax_i.legend()
        plt.tight_layout()


def plot_rate_estimate(controller: Controller):
    dom = [t / 60 / 60 for t in range(controller.clock.time)]
    fig, ax = plt.subplots(1, 1)
    fig.suptitle('Estimated vs True Traffic Rate')
    for i, (lane, col) in enumerate(zip(controller.lanes, mcolors.TABLEAU_COLORS)):
        rate_estimate = controller.state_hist[f'lane_{i}_wait_time']
        rate_true = [lane.traffic_rate_fn(t) for t in dom]
        ax.plot(dom, rate_estimate,  alpha=0.3, color=col)
        ax.plot(dom, rate_true, label=f'Lane {i+1}', color=col)

    ax.set_ylabel(f'Cars per minute')
    ax.set_xlabel(f'Time in hours')
    ax.legend()

    plt.show()
