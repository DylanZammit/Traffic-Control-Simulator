# Traffic Light Simulator
## Table of contents
1. [Introduction](#Introduction)
2. [Installation](#Model-Explanation)
3. [Running](#Code-Structure)
3. [Implementation](#Implementation)
4. [Srategies](#Data)
5. [Configuration](#Methodology)
6. [Results](#Results)
7. [Conclusion](#Improvements)

## Introduction
Commuting to and from work on a daily basis is a frustrating experience to say the least.
It is especially frustrating when you can pinpoint improvements in the traffic system, that can potentially easily be implemented.
One such annoyance is the Kennedy Drive traffic lights shown in the below google maps image (Coordinates: `35.9450, 14.4128`).

This is a 3-road junction, with each road having two lanes, and each traffic light having a duration of exactly 20 seconds
before switching from green to red (yes, I timed it multiple times while I am stuck in traffic).
![kennedy_drive](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/kennedy_drive.png?raw=true)
Spawning from this frustration, I would like to come up with a simple but optimal traffic-light strategy that can
possibly drastically improve the flow of traffic in this junction. This project creates a generic and easily 
configurable traffic simulation. It is set up in such a way that it is easy for one to implement their own strategy
and compare with other strategies. The following figure is an example of such comparisons between different strategies 
for the same traffic rates.
![flow_simulation](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim.png?raw=true)
## Installation
Before running the script, 
* Make sure that `python>=3.11 ` is being used and
* the necessary packages must be installed by first going to the root directory and running 
```bash
python -m pip install . -r reqiurements.txt
```
## Running
Then the following code can be used to run the script. The `config.yaml` file living in the same directory from which the python interpreter
is loaded shall contain all the configuration of the system and models.
```bash
python simulator.py
```
## Implementation
In this image we can see an example flow of traffic for a particular lane.
We can observe the cyclic effect, beginning with a 40-second period of worsening traffic.
This is typically followed by a duration of 20 seconds where vehicles are dispelled out of the queue,
usually at a higher rate than that of entry, explaining the steeper downward gradient. Despite this,
the 20-seconds is not enough to compensate for the 40-second incline in traffic. This generates an overall
upward trend in traffic.
![flow_simulation_closeup](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_incline.png?raw=true)
### Poisson Process
The flow of traffic across time is assumed to follow a Poisson Process. This model revolves around the Poisson distribution, which is a natural
distribution used to count random objects.  Another application of the Poisson distribution is used to model
the number of goals scored by a team in a football match. This in turn is used to model the probabilities of a team winning
an encounter against an opponent. An implementation and more detailed explanation is given in this [Github Project](https://github.com/DylanZammit/Football-Odds-Prediction).

There are two ways two define such a process.

* The first definition states that the duration between any two successive arrivals follows an exponential distribution with some rate parameter $`\lambda`$.
* The second definition states that for any time interval of length $`t`$ seconds, the number of cars arriving is Poisson distributed with mean parameter $`\lambda t`$.

The second definition is more relevant for the implementation of this project as shall be described in the next section. 
### Simulation
Each road is considered as being defined by a queue of cars incoming using a FIFO process. 

The brains of the system is defined in the `Controller` class. This will contain all of our universe's information such as

* the lanes and their metadata
* the cars which belong in a lane queue and in turn the controller
* the clock, which keeps track of the time taken since the beginning of the simulation
* the incoming/outgoing cars in all lanes
* the strategy deciding when a traffic light should turn green and for how long.

The controller is first defined, and the `run_iter` method is called iteratively in a loop for a desired duration.
Each iteration corresponds to 1 second in real-life. This method performs the following steps:
1) Increment the time by one second.
2) Update each lane with new incoming cars by sampling from a Poisson distribution with rate $`\lambda_i`$ for lane $`i`$.
3) If the last car in the current active lane exited $`1/\mu`$ seconds ago, then a car should exit.
4) Check if the current active lane should turn red based on the implemented strategy.
5) Optionally save any metadata for later analysis.

<details>
<summary>run_iter</summary>

```python
def run_iter(self) -> None:

    self.clock.tick()

    for lane in self.lanes:
        lane.update_new_active()

    num_active_cars = self.active_lane.num_active_cars
    time_since_last_exit = self.clock.time - self.active_lane.last_exit_time

    if num_active_cars > 0 and time_since_last_exit >= (1 / self.exit_rate):
        self.active_lane.drive_car()

    if self.is_time_up():
        self.run_next_lane()

    if self.save_hist:
        self.update_hist()
```

</details>

### Strategy Setup
The `Controller` class enforces implementation of the `is_time_up` method. This method should take all information
of the system, and return a boolean depending no whether it is time to switch lane or not. This is essentially the brain
of the model. Thus one would need to create their own child-controller class that inherits from `Controller`, implementing
at least this method (and optionally more if required).

For instance below is the simplest implemented method of the Baseline strategy that will be described in more detail in an
upcoming section.

<details>
<summary>Baseline Strategy</summary>

```python
class ConstantController(Controller):

    def __init__(self, wait_time: int, **kwargs):
        super().__init__(**kwargs)
        self.wait_time = wait_time

    def is_time_up(self) -> bool:
        is_max_time_elapsed = self.clock.diff(self.active_lane.active_since) > self.wait_time
        return is_max_time_elapsed
```

</details>

### Incoming Rate

The incoming car rate for lane $`i`$ is varied throughout the day in an attempt to capture the morning evening rush hours.

We would like to capture some important features:
* Morning rush hour peak at around 8am
* Evening rush hour peak at around 5pm
* A baseline traffic flow for the rest of the day

This rate is modelled by summing two beta distributions (since they have a domain between 0 and 1), scale it by 24 times
representing the whole day, and finally shifting up by a base traffic 

<details>
<summary>Traffic Rate Function</summary>

```python
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
```

</details>

### Assumptions
Below are some assumptions taken.

* Number of cars arriving follows a Poisson distribution.
* The exit rate is constant throughout the day, and it does not vary with the queue position of a car.
* There is no yellow light.
* All 3 lanes are independent of each other.

The above models are quite relaxed in general. It would be interesting if they could be somehow modelled, but I would imagine it
being quite difficult to do so. Consider for example the last point.
Lanes being dependent on each other might occur if other junctions such a roundabout is in the vicinity of the traffic lights.
In this case, one busy lane might clog up the roundabout, which in turn impacts the other lanes. 

## Strategies
In this experiment we will implement and compare 3 different strategies. I will explain the three models in the followign subsections.
### Baseline Model
This is the simplest model of the three, where the duration of each green light is exactly 20 seconds.
This replicates the behaviour of the traffic lights at Kennedy Drive, which I strongly suspect can be optimised.
What usually ends up happening, is that during the commute back to home, heavy traffic accumulates in the northbound direction of the junction.
The other two lanes, in comparison, have a low and steady rate of traffic.
Two natural question arise: 
* Does it make sense for all three lanes to be equally weighted?
* Does it make sense for the total duration of the three loops equal 60 seconds?
### Idle Model
As I look at the other cars in flowing lanes cruise by, or more frustratingly, watch all three lanes idle
while no cars are flowing in the green-lit lane, I wonder why that specific lane cannot simply turn red
so that busier lanes can start moving. This is exactly the strategy of this model. If, for at least P seconds
no cars enter the lane, the light automatically turns to red, so that other lanes can start moving.

This should almost certainly help the flow of traffic under low or medium traffic conditions. 

However, what happens when there is at least medium-to-high traffic? 
If $`P=5s`$ and all lanes see a new car at a relatively low rate of 4 seconds, then this model is precisely equivalent
to the Baseline model. The next model attempts to address this issue.
### Snapshot Model
This model attempts to use the rate of incoming cars to dynamically adjust the ratio of light duration between all lanes.
Define the following variables:
* $`M`$: number of lanes,
* $`\lambda_i`$: car entry rate per minute for lane $`i`$,
* $`\mu`$: car exit rate per minute,
* $`t_i`$: proportion of time spent green for lane $`i`$.

From the above definitions, the following points follow:
* $`t_1 + ... + t_M = 1`$,
* $`\mu \cdot t_i`$ is the average exit rate per loop for lane $`i`$,
* $`max(0, \lambda_i - \mu * t_i)`$ is the average car entry differential per loop for lane $`i`$.

Thus, a natural objective function that we would like to minimise over
the vector $`t=(t_1, .., t_M)`$ is the *overall* average minutely car entry differential.
```math
L(t_1, \cdots, t_M) = \min_{t_1, \cdots, t_M} \sum_{i=1}^M \max(0, \lambda_i - \mu * t_i) ^ 2
```
Notice that squaring the inner component is essential, as otherwise
the minimising solution would be to simply set $`t_i = 0`$ for all $`i`$ except
$`t_j=1`$, where $`j`$ is the lane with the lowest rate of cars flowing in.

This optimisation problem is run at the start of every loop, i.e. just before the first lane turns green.
The outcome of the model is noted, and the current loop of lanes will use this result as waiting times.

Another advantage of this model is that it is relatively simple to implement.
All that is required is a count of cars flowing through a lane,
the technology for which to do so already exists.
## Configuration
A full 24-hour day is simulated where the exit rate is set to 1 car per second.
How did I get to this figure? While stuck in traffic, I simply counted the number of cars
in front of me, and then counted how long it took me to reach the first position. 
Dividing the two roughly resulted in a rate of one car exit every two seconds.
Since all lanes of this junction are dual-carriageways, the rate of 0.5 was multiplied by 2 to get a value of $`\mu=1`$.

A separate bimodal traffic rate was created to simulate the varying flow of traffic throughout the day for each separate lane.
The bimodal nature reflects the increased spikes of traffic in the morning and afternoon rush
corresponding to many people's commute to/from work.
A figure below displays these curves with the real-time rate estimate superimposed.

The junction is assumed to have 3 lanes, just like the Kennedy Drive junction.

The three models were configured with the below parameters.
* Baseline model: 20 seconds each green light
* Idle model: 20 seconds each green light, which turns off immediately if 5 seconds of unobserved cars occur.
* Snapshot model: a lookback of 5 minutes to estimate the rate of incoming cars, and a total loop duration of 1 minute. This one minute will be apportioned according to the minimising function.

Below is the yaml file including all of this configuration.

<details>
<summary>Example Config File</summary>

```yaml
simulation:
    shared:
        n_sim: 1
        duration_hours: 24
        exit_rate: 1
        frustration_fn: quad
        verbose: False
        save_hist: True
        lanes_config:
            -
                morning_peak_rate: 10
                evening_peak_rate: 20
            -
                morning_peak_rate: 15
                evening_peak_rate: 15
            -
                morning_peak_rate: 20
                evening_peak_rate: 10
    models:

        Baseline_20s:
            controller: ConstantController
            wait_time: 20

        Idle_10s_5s:
            controller: IdleController
            wait_time: 20
            idle_time: 5

        snapshot_controller:
            controller: SnapshotController
            rate_lookback: 300
            loop_duration: 60
```
</details>

## Results

Before describing the following figures, we define what is "frustration" in this context.
Consider a car $`c_{ij}`$ in lane $`i`$ and position $`j`$ waiting in traffic for $`w_ij`$ seconds.
The frustration of this car is defined to be $`w_{ij} ^ 2`$. Squaring the wait time helps reflect
that people tend to not mind stopping and waiting for a couple of seconds, but get
increasingly frustrated (at a non-linear rate) the more they wait. The total frustration
is then simply the sum of all $`w_{ij} ^ 2`$ for all $`i`$ and all $`j`$.

The below image shows the entry rate of cars per minute in every lane. 
Superimposed on this is the empirically estimated entry rate based on the past 5 minutes.
This estimate is used in the Snapshot model as described above to create
a dynamic traffic light waiting time.

![true_estimate_rate](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/true_estimate_rate.png?raw=true)

Below are the simulation results of different strategies described in the above section. 
The lines correspond to the cars waiting for the green light for every separate lane. 
The values were smoothed using a windows of 5 minutes for readability.

![flow_case_1](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_case_max20.png?raw=true)

This model clearly shows (unsurprisingly) that the worst model out of the three is the baseline model.
The average car frustration is at 0.3, more than twice the other two strategies. 
Also note the drastic increase in cars waiting in traffic during the morning and evening rush hours.
Although visible, it is much less evident in the other two models, reaching half the queued cars at the peak.

The Idle model and Snapshot model are much more comparable, with the frustration score being similar. 
However, what happens when we increase the flow of cars at the peak of rush hour by a little bit?
The below image shows the same simulation with the only difference being that the entry rate at the peak
rush hour times is increased from 20 to 22 cars per minute.

![flow_case_2](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_case_max25.png?raw=true)

As described earlier, the baseline and idle models become much more similar to each other with increased traffic.
The baseline model is extremely susceptible to heavy traffic with an increased flow of traffic, reaching a peak of 300 
cars waiting for Lane 3 at around 10am.
The snapshot model, on the other hand, adjusted impressively well to the flow of traffic,
alleviating the burden of traffic across all three lanes throughout the day, with no
parameter tuning at all. All 3 lanes seem to have similar levels of traffic. The idle model in comparison has visible 
spikes during rush hours. However, during quiter periods throughout the day, performs better than the Snapshot model.

This not only shows that the model is comparable or superior to the other two in terms of "frustration metrics".
It also shows that it is much more robust to traffic conditions due to its dynamic nature. 
It might make sense to combine the snapshot model with the idle model depending on the time of day for an even 
better model.

## Conclusion

Hopefully this project sheds some (more) light on the obviously worsening traffic conditions in Malta.
Moreover, I hope that such a project inspires greater minds into realising that the traffic problem in Malta
is solvable, or at the very least improvable with relatively simple changes.