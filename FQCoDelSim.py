'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import salabim as sim
import random

print "\n\n****************************************************************************"
print "**                         COPYRIGHT NOTICE                               **"
print "**                                                                        **"
print "**  This program is free software: you can redistribute it and/or modify  **"
print "**  it under the terms of the GNU General Public License as published by  **"
print "**  the Free Software Foundation, either version 3 of the License, or     **"
print "**  (at your option) any later version.                                   **"
print "**                                                                        **"
print "**  This program is distributed in the hope that it will be useful,       **"
print "**  but WITHOUT ANY WARRANTY; without even the implied warranty of        **"
print "**  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         **"
print "**  GNU General Public License for more details.                          **"
print "**                                                                        **"
print "**  You should have received a copy of the GNU General Public License     **"
print "**  along with this program.  If not, see <http://www.gnu.org/licenses/>. **"
print "**                                                                        **"
print "****************************************************************************\n\n"








UNCLAIMED = -1

MSS = 1500.0 * 8.0
QUANTUM = MSS + (18.0 * 8.0)
old = False

class genFlow(sim.Component):
    def process(self, waitTime):
        for i in range(0,2*SPARSEFLOWS,2):               
            sparseFlowGenerator(fid=i,interTime=time*INTERARRIVALMULTIPLIER, distribution="uniform")
            yield self.hold(sim.Exponential(waitTime/SPARSEFLOWS).sample())


class sparseFlowGenerator(sim.Component):
    def process(self,fid, interTime, distribution="uniform"):
        spSize = 0
        
        if int(SPARSESIZE) == -1 * 8:
            spSize = QUANTUM/2
        else:
            spSize = SPARSESIZE

        if distribution is "uniform":
            while True:
                flow(name='sflow-' + str(fid), fid=fid, size = spSize )
                yield self.hold(interTime)

        elif distribution is "exponential":
            while True:
                flow(name='sflow-' + str(fid), fid=fid, size = spSize)
                yield self.hold(sim.Exponential(interTime).sample())
        
        else:
            print("INVALID DISTRIBUTION")
            yield self.cancel


class bulkFlowGenerator(sim.Component):
    def process(self,fid, interTime, distribution="uniform"):
       
        if distribution is "uniform":
            while True:
                flow(name='bflow-' + str(fid), fid=fid, size=QUANTUM)
                yield self.hold(interTime)

        elif distribution is "exponential":
            while True:
                flow(name='bflow-' + str(fid), fid=fid, size=QUANTUM)
                yield self.hold(sim.Exponential(interTime).sample())
        
        else:
            print("INVALID DISTRIBUTION")
            yield self.cancel


class flow(sim.Component):
    def setup(self, fid, size):
        self.fid = fid
        self.packetSize = size - (size % 8)
        self.timeOfArrival = env.now()
        self.timeOfRemoval = 0.0

    def process(self):
        global old 
        for i in range(len(newQueues)):
            if newQueues[i].qid is self.fid:
                newQueues[i].push(self)
                newQueues[i].packetCounter += 1
                yield self.cancel()

        for j in range(len(oldQueues)):
            if oldQueues[j].qid is self.fid:
                oldQueues[j].push(self)
                oldQueues[j].packetCounter += 1
                yield self.cancel()

        for k in range(len(passiveQueues)):
            if passiveQueues[k].qid is self.fid:
                passiveQueues[k].push(self)
                passiveQueues[k].packetCounter += 1
                passiveQueues[k].activateCounter += 1
                passiveQueues[k].move(passiveQueues, newQueues) 
                old = False

                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()
        
        for l in range(len(passiveQueues)):
            if passiveQueues[l].qid is UNCLAIMED:
                passiveQueues[l].push(self)
                passiveQueues[l].qid = self.fid
                passiveQueues[l].move(passiveQueues, newQueues)

                old = False
                
                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()

        print "No available queues\n" 
        yield self.cancel()
        
    def timeInQueue(self):

        return (self.timeOfRemoval - self.timeOfArrival)

class queue(sim.Component):
    def setup(self):
        self.queue = sim.Queue()
        self.credits = QUANTUM
        self.sparse = False
        self.qid = UNCLAIMED
        self.packetCounter = 0.0
        self.activateCounter = 0.0
        self.totalQueueDelay = 0.0

    def move(self, source, destination):
        self.leave(source)
        self.enter(destination)
    
    def push(self, component):
        component.enter(self.queue)

    def resetCredits(self):
        self.credits = QUANTUM

    def addDelay(self):
        self.queue[0].timeOfRemoval = env.now()
        self.totalQueueDelay += self.queue[0].timeInQueue()


class scheduler(sim.Component):
    def process(self):
        counter = 0
        global old
        old = False

        while True:
            
            if not old:
                if not newQueues:
                    old = True
                
                else:
                    queue = newQueues[0].queue
                
                    while newQueues[0].credits > 0 and queue:

                        newQueues[0].credits -= queue[0].packetSize
                    
                        clerk.activate(queue=newQueues[0], size=queue[0].packetSize)
                        yield self.passivate()
                
                    if newQueues[0].credits <= 0:
                        newQueues[0].credits += QUANTUM

                    
                    newQueues[0].move(newQueues, oldQueues)
                    counter = 0

            elif oldQueues and old:
                queue = oldQueues[0].queue
                 
                if queue:
                    while oldQueues[0].credits > 0 and queue:
                        
                        oldQueues[0].credits -= queue[0].packetSize
                        clerk.activate(queue=oldQueues[0], size=queue[0].packetSize)
                        yield self.passivate()
                        counter += 1
                        
                    if oldQueues[0].credits <= 0:
                        oldQueues[0].credits += QUANTUM
                    
                    oldQueues[0].move(oldQueues, oldQueues)
                    
                else:
                    oldQueues[0].resetCredits()
                    oldQueues[0].move(oldQueues, passiveQueues)
                    old = True
                
            

            elif not self.ispassive():
                yield self.passivate()

            if counter == len(oldQueues) and old:
                counter = 0
                



class clerk(sim.Component):
    def process(self, queue, size):
        while True:
            queue.addDelay()
            queue.queue.pop()
            scheduler.activate(delay=(size/BANDWIDTH))
            yield self.cancel()



while True:
    BANDWIDTH = input("Enter bandwidth (Mbps): ") * pow(10,6)
    if BANDWIDTH > 0:
        break
    print "invalid input, try again!"

while True:
    SPARSEFLOWS = input("Enter number of sparseflows: ")
    if SPARSEFLOWS > 0:
       break
    print "invalid input, try again!"

while True:
    SPARSESIZE = input("Enter sparseflow packetsize(Byte): ") * 8.0
    if SPARSESIZE > 0 or SPARSESIZE == -1:
        break
    print "invalid input, try again!"
while True:
    BULKFLOWS = input("Enter number of bulkflows: ")
    if BULKFLOWS >= 0:
        break
    print "invalid input, try again!"

while True:
    INTERARRIVALTIME = input("Enter interarrival time(ms): ") * pow(10,-3)
    if INTERARRIVALTIME > 0 or INTERARRIVALTIME == -1:
        break
    print "invalid input, try again!"

while True:
    INTERARRIVALMULTIPLIER = input("Enter interarrivaltime multiplier ")
    if INTERARRIVALMULTIPLIER > 0:
        break
    print "invalid input, try again!"

while True:
    RUNTIME = input("Enter simulated runtime: ")
    if RUNTIME > 0:
        break
    print "invalid input, try again!"

while True:
    DETAILEDOUTPUT = input("Detailed output?: ")
    if DETAILEDOUTPUT == 0 or DETAILEDOUTPUT == 1:
        break
    print "invalid input, try again!"

while True:
    TRACE = input("Trace?: ")
    if TRACE == 0 or TRACE == 1:
        break
    print "invalid input, try again!"




def sparseCalc():
    if int(SPARSESIZE) == -1 * 8:
        return ((QUANTUM*(BULKFLOWS + 1)) + ((SPARSEFLOWS*QUANTUM)/2.0))/BANDWIDTH
    
    else:
        return ((QUANTUM*(BULKFLOWS + 1)) + (SPARSEFLOWS*SPARSESIZE))/BANDWIDTH


def printQueueDelay(detailed = False):
    averageWaitingTime = 0.0

    if detailed:
	print "+----------+--------------+-----------+"
	print "| Flow id: | Sparseness % | Time (ms) |"
	print "+----------+--------------+-----------+"
	
    for x in range(len(passiveQueues)):
        if int(passiveQueues[x].packetCounter) == 0:
            print "| ", str(passiveQueues[x].qid).ljust(6), "Did not activate".ljust(18), " | "
            continue

        if detailed:
            print "| ", str(passiveQueues[x].qid).ljust(6), " |",
            print " ", str(round((passiveQueues[x].activateCounter / passiveQueues[x].packetCounter) * 100, 4)).ljust(9), " |", 
            print " ", str(round((passiveQueues[x].totalQueueDelay / passiveQueues[x].packetCounter) * 1000, 4)).ljust(6), " |"
            print "+----------+--------------+-----------+"

        if passiveQueues[x].qid % 2 == 0:
            averageWaitingTime += passiveQueues[x].totalQueueDelay/passiveQueues[x].packetCounter


    for x in range(len(newQueues)):
        if detailed:
            print "| ", str(newQueues[x].qid).ljust(6), " |",
            print " ", str(round((newQueues[x].activateCounter / newQueues[x].packetCounter) * 100, 4)).ljust(9), " |", 
            print " ", str(round((newQueues[x].totalQueueDelay / newQueues[x].packetCounter) * 1000, 4)).ljust(6), " |"
            print "+----------+--------------+-----------+"
            

        if newQueues[x].qid % 2 == 0:
            averageWaitingTime += newQueues[x].totalQueueDelay/newQueues[x].packetCounter 


    for x in range(len(oldQueues)):
        if detailed:
            print "| ", str(oldQueues[x].qid).ljust(6), " |",
            print " ", str(round((oldQueues[x].activateCounter / oldQueues[x].packetCounter) * 100, 4)).ljust(9), " |", 
            print " ", str(round((oldQueues[x].totalQueueDelay / oldQueues[x].packetCounter) * 1000, 4)).ljust(6), " |"
            print "+----------+--------------+-----------+"
            
	if oldQueues[x].qid % 2 == 0:
            averageWaitingTime += oldQueues[x].totalQueueDelay/oldQueues[x].packetCounter

    if SPARSEFLOWS != 0:
        print "\nAverage queueing delay per sparseflow: ", round((averageWaitingTime/SPARSEFLOWS)*1000, 4), "ms"





env = sim.Environment(trace=TRACE,random_seed=None)


scheduler = scheduler()

if int(INTERARRIVALTIME * 1000) == -1:
    time = sparseCalc()

else:
    time = INTERARRIVALTIME

passiveQueues = sim.Queue('passiveQueues')

for _ in range(SPARSEFLOWS + BULKFLOWS):
        queue().enter(passiveQueues)

gen = genFlow(waitTime=time)
        
for i in range(1,2*BULKFLOWS,2):
    bulkFlowGenerator(fid=i,interTime=((QUANTUM/BANDWIDTH)-(1.0/BANDWIDTH)),distribution="uniform")




newQueues = sim.Queue('newQueues')
oldQueues = sim.Queue('oldQueues')


clerk = clerk(process=None)

env.run(till=RUNTIME)



printQueueDelay(DETAILEDOUTPUT)

