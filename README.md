# FQ-CoDel sparseflow optimisation simulator

This simulator was written as a project at Karlstad University in Sweden. The program simulates the behaviour of the FQ-CoDel sparseflow optimisation algorithm in different scenarios. 
The simulator is used to obtain queueing latency aswell as a percentage value of how often a flow get the sparseflow treatment, this can be done for many different scenarios. 
The scenarios is fully customizable by the user and everything from bandwidth to packetsize can be changed between the runs. Results from different simulation runs in 
both table and graph form can be found in [FqCoDel.pdf](FqCoDel.pdf).



### Simplifications 
Since we are only interested in simulating the behaviour of the sparseflow optimisation mechanism the following simplifications was made. 

* No hashing of the flows - Since hashcollisions is very rare we assume that each individual flow receives their own queue

* Unlimited queues - Since we are interested in the sparseflow optimisation mechanism there is no need to care about dropping packets. The bulkflows should 
always have packets in the queue and the sparseflows should never have to drop a packet. If a sparseflow would have to drop a packet it wouldn't be classified as sparse anyaway. 

### Prerequisites

The program have only been tested on a virtual machine running Ubuntu 17.04 so we can't garuantee that it works on any other OS. 

Python 2.7:
If it is not already installed you can install it by typing

**sudo add-apt-repository ppa:fkrull/deadsnakes-python2.7**

**sudo apt-get update** 

**sudo apt-get install python2.7**

in the terminal. 

If a newer version of python is prefered we can't garuantee that the code works as intended. 

Salabim library:

Use pip to install the Salabim library by typing

**pip install salabim**

in the terminal. 

### Running the program

Type

**python FQCoDelSim.py** 

in the terminal and follow these instructions.
 
**Bandwidth** - Type the desired bandwidth in Mbps. E.g write "10" if you want 10 Mbps

**Number of sparseflows** - Type the number of sparseflows you want

**Sparseflow packetsize** - Type the packetsize of the sparseflow in bytes. E.g typ "500" if you want 500 MB packetsize, can type "-1" if you want to use a 
built in function

**Number of bulkflows** - Type the number of bulkflows you want

**Interarrivaltime** - Type the desired intervall in ms between the packets in a flow. E.g type "20" if you want 20 ms in interarrival time, can type "-1" to 
use built in function

**Interarrival multiplier** - Type the multiplier to the interarrival time. E.g if you want 2x the interarrival time type a "2".

**Runtime** - Type the number of seconds you want to simulate. E.g type "100" if you want to simulate 100 seconds

**Detailed output** - Type 1 for a more detailed output that includes how many packets (in %) that get the sparseflow treatment, the average queueing time for a packet in that flow and the average 
waiting time for all of the flows. Type 0 to just get the average waiting time for all of the flows. 

**Trace** - Type "1" if you want to trace everything or type "0" if you don't. 

## Output

For each flow the "sparseness percent", which is the percentage of packages that get the sparseflow treatment is given. 
The average waiting time for a packet in the particular flow is also given. 

The last thing in the output is the average waiting time for a flow


## Built With

* [Salabim](http://www.salabim.org/manual/index.html#) - The simulator library




## Authors

* **Daniel Larsson** - *Main developer* - *Email: daniellarsson054@gmail.com*
* **Martin Wahlberg** - *Main developer* - *Email: martin_p95@hotmail.se*



## License

This project is licensed under the GNU GPL License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* **Johan Garcia** - *Supervisor*
* **Toke Høiland-Jørgensen** - *Supervisor*
