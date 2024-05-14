from typing import Self, Any, Callable
from functools import wraps, cache
import time
import numpy as np
from scipy.stats import beta


class Clock:
    """
    Class representing a simple clock for time tracking.

    Parameters
    ----------
    step : int
        Time step increment for the clock.

    Attributes
    ----------
    time : int
        Current time tracked by the clock.
    step : int
        Time step increment for the clock.

    Methods
    -------
    tick() -> Self
        Increment the time by the step size.
    diff(t) -> int
        Calculate the difference between the current time and a given time.

    Notes
    -----
    This class provides a simple clock mechanism for time tracking with basic time manipulation methods.
    """

    def __init__(self, step: int = 1):
        self.time = 0
        self.step = step

    def tick(self) -> Self:
        self.time += self.step
        return self

    def diff(self, t) -> int:
        return self.time - t


def print_padding(text: Any, pad_char: str = '*', string_len: int = 50) -> None:
    """
    A function to print text surrounded by padding characters to a specified string length.

    Parameters:
    ----------
    text : Any
        The text to be printed.
    pad_char : str, optional
        The character used for padding, default is '*'.
    string_len : int, optional
        The total length of the output string, default is 50.

    Returns:
    -------
    None
    """
    n_text = len(str(text))

    padding = pad_char * ((string_len - n_text) // 2 - 2)

    print(f'{padding} {text} {padding}')


def timer(func: Callable) -> Callable:
    """
    A decorator that measures the duration of a function call and prints the duration.

    Parameters:
    ----------
    func: Callable
        The function to be timed.

    Returns:
    -------
    Callable
        A wrapped function that executes the input function and prints the duration.
    """
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
    """
    A function to calculate the traffic rate based on various parameters such as time of day, peak times, and rates.

    Parameters:
    ----------
    t_hours: float
        The time in hours.
    morning_peak_time: float, default 8
        The time of the morning peak.
    morning_peak_rate: float, default 50
        The rate during the morning peak.
    evening_peak_time: float, default 17
        The time of the evening peak.
    evening_peak_rate: float, default 40
        The rate during the evening peak.
    baseline_night_rate: float, default 5
        The baseline rate at night.

    Returns:
    -------
    float
        The calculated traffic rate based on the input parameters.
    """
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
