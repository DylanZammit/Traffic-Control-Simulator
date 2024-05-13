# Traffic Light Simulator
## Table of contents
1. [Introduction](#Introduction)
2. [Installation](#Model-Explanation)
3. [Running](#Code-Structure)
4. [Srategies](#Data)
5. [Configuration](#Methodology)
6. [Results](#Results)
7. [Conclusion](#Improvements)

## Introduction
Commuting to and from work on a daily basis is a frustrating experience to say the least.
It is especially frustrating when you can pinpoint improvements in the traffic system, that can potentially easily be implemented.
One such annoyance is the Kennedy Drive traffic lights shown in the below google maps image.

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
## Implementation [WIP]
In this image we can see an example flow of traffic for a particular lane.
We can observe the cyclic effect, beginning with a 40-second period of worsening traffic.
This is typically followed by a duration of 20 seconds where vehicles are dispelled out of the queue,
usually at a higher rate than that of entry, explaining the steeper downward gradient. Despite this,
the 20-seconds is not enough to compensate for the 40-second incline in traffic. This generates an overall
upward trend in traffic.
![flow_simulation_closeup](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_incline.png?raw=true)
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
so that more trafficous lanes can start moving. This is exactly the strategy of this model. If, for at least P seconds
no cars enter the lane, the light automatically turns to red, so that other lanes can start moving.

This should almost certainly help the flow of traffic under low or medium traffic conditions. 

However, what happens when there is at least medium-to-high traffic? 
If P=5s and all lanes see a new car at a relatively low rate of 4 seconds, then this model is precisely equivalent
to the Baseline model. The next model attempts to address this issue.
### Snapshot Model
This model attempts to use the rate of incoming cars to dynamically adjust the ratio of light duration between all lanes.
Define the following variables:
* `M`: number of lanes,
* `L_i`: car entry rate per minute for lane `i`,
* `mu`: car exit rate per minute,
* `t_i`: proportion of time spent green for lane `i`.

From the above definitions, the following points follow:
* `t_1 + ... + t_M = 1`,
* `mu * t_i` is the average exit rate per loop for lane `i`,
* `max(0, L_i - mu * t_i)` is the average car entry differential per loop for lane `i`.

Thus, a natural objective function that we would like to minimise over
the vector `t=(t_1, .., t_M)` is the *overall* average minutely car entry differential.
```math
\min_t \sum_1^M [ \max(0, \lambda_i - \mu * t_i) ^ 2]
```
Notice that squaring the inner component is essential, as otherwise
the minimising solution would be to simply set `t_i = 0` for all `i` except
`t_j=1`, where `j` is the lane with the lowest rate of cars flowing in.

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
Since this junction has two lanes, I multiplied the rate of 0.5 by 2 to get a value of `mu=1`.

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
<summary>Output</summary>

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
Consider a car `c_ij` in lane `i` and position `j` waiting in traffic for `w_ij` seconds.
The frustration of this car is defined to be `w_ij ^ 2`. Squaring the wait time helps reflect
that people tend to not mind stopping and waiting for a couple of seconds, but get
increasingly frustrated (at a non-linear rate) the more they wait. The total frustration
is then simply the sum of all `w_ij ^ 2` for all `i` and all `j`.

The below image shows the entry rate of cars per minute in every lane. 
Superimposed on this is the empirically estimated entry rate based on the past 5 minutes.
This estimate is used in the Snapshot model as described above to create
a dynamic traffic light waiting time.

![true_estimate_rate](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/true_estimate_rate.png?raw=true)

Below are the simulation results of different strategies described in the above section. 
The black line shows the total number of cars waiting in the roads across all lanes
whereas the other lines correspond to the cars waiting for the green light for every separate lane.

![flow_case_1](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_case_max20.png?raw=true)

This model clearly shows (unsurprisingly) that the worst model out of the three is the baseline model.
The average car frustration is at 0.62, more than 4 times the other two strategies. 
Also note the drastic increase in cars waiting in traffic during the morning and evening rush hours.
Although visible, it is much less evident in the other two models, reaching half the queued cars at the peak.

The Idle model and Snapshot model are much more comparable, with the frustration score being similar. 
However, what happens when we increase the flow of cars at the peak of rush hour by a little bit?
The below image shows the same simulation with the only difference being that the entry rate at the peak
rush hour times is increased from 20 to 25 cars per minute.

![flow_case_2](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_case_max25.png?raw=true)

As described earlier, the baseline and idle models become much more similar to each other with increased traffic.
It is still worth noting that the Baseline model is the worst of the three.
The snapshot model, on the other hand, adjusted impressively well to the flow of traffic,
alleviating the burden of traffic across all three lanes throughout the day, with no
parameter tuning at all.

This not only shows that the model is superior to the other two in terms of "frustration metrics".
It also shows that it is much more robust to traffic conditions due to its dynamic nature.

## Conclusion

Hopefully this project sheds some (more) light on the obviously worsening traffic conditions in Malta.
Moreover, I hope that such a project inspires greater minds into realising that the traffic problem in Malta
is solveable, or at the very least improveable with relatively simple changes.