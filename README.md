# Project Title

This simulator was written as a project at Karlstad University. The program simulates the behaviour of the FQ-CoDel algorithm in different scenarios. 
The simulator was used to obtain queueing latency aswell as percentage value of how often a flow got the sparseflow treatment, this was done for a different number of scenarios. 
The scenarios is fully customizable by the user and everything from bandwidth to packetsize can be changed between the runs. Simulation results in
both table and graph form can be found in [INSERT REPORT HERE].


### Prerequisites

The program have only been tested on a virtual machine running Ubuntu [SOME VERSION] so we can't garuantee that it works on any other OS. 

Python 2.7:
If it is not already installed you can install it by typing

sudo add-apt-repository ppa:fkrull/deadsnakes-python2.7

sudo apt-get update 

sudo apt-get install python2.7

in the terminal. 

If a newer version of python is prefered we can't garuantee that the code works as intended. 

Salabim framework:

Use pip to install the Salabim framework by typing

pip install salabim 

in the terminal. 

### Running the program

Type

python [INSERT FILENNAME HERE] 

in the terminal and follow these instructions.
 
Bandwidth - Type the desired bandwidth in Mbps. E.g write "10" if you want 10 Mbps

Number of sparseflows - Type the number of sparseflows you want

Sparseflow packetsize - Type the packetsize of the sparseflow in bytes. E.g typ "500" if you want 500 MB packetsize, can type "-1" if you want to use a 
built in function

Number of bulkflows - Type the number of bulkflows you want

Interarrivaltime - Type the desired intervall in ms between the packets in a flow. E.g type "20" if you want 20 ms in interarrival time, can type "-1" to 
use built in function

Interarrival multiplier - Type the multiplier to the interarrival time. E.g if you want 2x the interarrival time type a "2".

Runtime - Type the number of seconds you want to simulate. E.g type "100" if you want to simulate 100 seconds

Trace - Type "1" if you want to trace everything or type "0" if you don't. 

## Output

For each flow the "sparseness percent", which is the percentage of packages that get the sparseflow treatment is given. 
The average waiting time for a packet in the particular flow is also given. 

The last thing in the output is the average waiting time for a flow





## Built With

* [Salabim](http://www.salabim.org/manual/index.html#) - The simulator framework




## Authors

* **Daniel Larsson** - *Main developer* - *Email: daniellarsson054@gmail.com*
* **Martin Wahlberg** - *Main developer* -*Email: martin_p95@hotmail.com*



## License

This project is licensed under the GNU GPL License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* **Johan Garcia** - *Supervisor*
* **Toke Høiland-Jørgensen** - *Supervisor*
