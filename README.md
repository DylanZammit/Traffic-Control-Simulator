# Traffic Light Simulator
TODO: give brief description of project here.

## Installation
Before running the script, 
* Make sure that `python>=3.11 ` is being used and
* the necessary packages must be installed by first going to the root directory and running 
```bash
python -m pip install . -r reqiurements.txt
```
## Running [WIP]
Then the following code can be used to run the script.
```bash
python simulator.py \
    --arg1 val1 \
    --arg2 val2 \
    --arg3 val3
```
## Implementation [WIP]
In this image we can see an example flow of traffic for a particular lane.
We can observe the cyclic effect, beginning with a 40-second period of worsening traffic.
This is typically followed by a duration of 20 seconds where vehicles are dispelled out of the queue,
usually at a higher rate than that of entry, explaining the steeper downward gradient. Despite this,
the 20-seconds is not enough to compensate for the 40-second incline in traffic. This generates an overall
upward trend in traffic.
![flow_simulation_closeup](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim_incline.png?raw=true)
## Strategies [WIP]
## Results [WIP]
Below are the simulation results of different strategies described in the above section (WIP). 
The black line shows the total number of cars waiting in the roads across all lanes.
![flow_simulation](https://github.com/DylanZammit/Traffic-Control-Simulator/blob/master/img/flow_sim.png?raw=true)
