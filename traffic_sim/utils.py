from typing import Self, Any, Callable
from functools import wraps, cache
import time
import numpy as np
from scipy.stats import beta


class Clock:

    def __init__(self, step: int = 1):
        self.time = 0
        self.step = step

    def tick(self) -> Self:
        self.time += self.step
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


@cache
def traffic_rate(
        t_hours: float,
        morning_peak_time: float = 8,
        morning_peak_rate: float = 50,
        evening_peak_time: float = 17,
        evening_peak_rate: float = 40,
        baseline_night_rate: float = 5,
) -> float:

    t_hours = t_hours % 24

    t_beta = t_hours / 24
    r = morning_peak_time / 24
    b_morning = 10
    a_morning = - ((b_morning - 2) * r + 1) / (r - 1)

    r = evening_peak_time / 24
    b_evening = 10
    a_evening = - ((b_evening - 2) * r + 1) / (r - 1)

    mode_morning = beta.pdf((a_morning - 1) / (a_morning + b_morning - 2), a_morning, b_morning)
    mode_evening = beta.pdf((a_evening - 1) / (a_evening + b_evening - 2), a_evening, b_evening)

    morning_rate = beta.pdf(t_beta, a_morning, b_morning) / mode_morning * (morning_peak_rate - baseline_night_rate)
    evening_rate = beta.pdf(t_beta, a_evening, b_evening) / mode_evening * (evening_peak_rate - baseline_night_rate)

    return baseline_night_rate + morning_rate + evening_rate


FRUSTRATION_MAP = {
    'quad': quadratic_frustration_fn,
    'expon': expon_frustration_fn
}


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    # Create an array of times from 0 to 24 hours (with fine resolution)
    times = np.linspace(0, 24, 1000)

    # Calculate traffic rates for these times
    rates = [traffic_rate(t) * 60 for t in times]

    # Plotting the function
    plt.figure(figsize=(10, 5))
    plt.plot(times, rates)
    plt.title('Traffic Rate Throughout the Day')
    plt.xlabel('Time (hours)')
    plt.ylabel('Rate of Incoming Cars (cars/hour)')
    plt.grid(True)
    plt.show()
