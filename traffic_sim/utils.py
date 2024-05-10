from typing import Self, Any, Dict, Callable
from functools import wraps
import time
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np


class Clock:

    def __init__(self):
        self.time = 0

    def tick(self) -> Self:
        self.time += 1
        return self

    def diff(self, t) -> int:
        return self.time - t


def print_padding(text: Any, pad_char: str = '*', string_len: int = 50) -> None:
    n_text = len(str(text))

    padding = pad_char * ((string_len - n_text) // 2 - 2)

    print(f'{padding} {text} {padding}')


def timer(func: Callable) -> Callable:

    @wraps(func)
    def wrapper(*args, **kwargs):
        tick = time.time()
        out = func(*args, **kwargs)
        tock = time.time()
        print(f'{func.__name__} duration: {tock - tick:.2f}s')
        return out

    return wrapper


def quadratic_frustration_fn(x) -> float:
    return (x / 60) ** 2


def expon_frustration_fn(x, k: float = 1) -> float:
    return np.exp(k * (x / 60)) - 1


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
    plt.show()
