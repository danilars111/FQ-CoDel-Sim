import salabim as sim
import random

UNCLAIMED = -1
BANDWIDTH = input("Enter bandwidth (Mbps): ") * pow(10,6)
SPARSEFLOWS = input("Enter number of sparseflows: ")
SPARSESIZE = input("Enter sparseflow packetsize(Byte): ") * 8.0
BULKFLOWS = input("Enter number of bulkflows: ")
MSS = 1500.0 * 8.0
QUANTUM = MSS + (18.0 * 8.0)
INTERARRIVALTIME = input("Enter interarrival time(ms): ") * pow(10,-3)
INTERARRIVALMULTIPLIER = input("Enter interarrivaltime multiplier ")
RUNTIME = input("Enter simulated runtime: ")
TRACE = input("Trace?: ")
old = False

def sparseCalc():
    if int(SPARSESIZE) == -1 * 8:
        return ((QUANTUM*(BULKFLOWS + 1)) + ((SPARSEFLOWS*QUANTUM)/2.0))/BANDWIDTH
    
    else:
        return ((QUANTUM*(BULKFLOWS + 1)) + (SPARSEFLOWS*SPARSESIZE))/BANDWIDTH


class sparseFlowGenerator(sim.Component):
    def process(self,fid, interTime, distribution="uniform"):
        #print("hold time: ",interTime/SPARSEFLOWS)
        yield self.hold(sim.Exponential(interTime/SPARSEFLOWS).sample())
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
               # print("Flow: ",oldQueues[j].qid,"enter in old")
                oldQueues[j].push(self)
                oldQueues[j].packetCounter += 1
                yield self.cancel()

        for k in range(len(passiveQueues)):
            if passiveQueues[k].qid is self.fid:
                passiveQueues[k].push(self)
                passiveQueues[k].packetCounter += 1
                passiveQueues[k].activateCounter += 1
                #print("Flow:",passiveQueues[k].qid,"activate ++")
                passiveQueues[k].move(passiveQueues, newQueues) 
                old = False

                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()
        
        for l in range(len(passiveQueues)):
            if passiveQueues[l].qid is UNCLAIMED:
                passiveQueues[l].push(self)
                passiveQueues[l].qid = self.fid
                #passiveQueues[l].packetCounter += 1
                #passiveQueues[l].activateCounter += 1
                passiveQueues[l].move(passiveQueues, newQueues)

                old = False
                
                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()

        print("No available queues\n")
        yield self.cancel()
        
    def timeInQueue(self):
        return (self.timeOfRemoval - self.timeOfArrival)

class queue(sim.Component):
    def setup(self):
        self.queue = sim.Queue()
        self.credits = QUANTUM
        self.new = True
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
   # def sparseIncrease(self):


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


env = sim.Environment(trace=TRACE,random_seed=None)


scheduler = scheduler()

if int(INTERARRIVALTIME * 1000) == -1:
    time = sparseCalc()

else:
    time = INTERARRIVALTIME

print(time)
passiveQueues = sim.Queue('passiveQueues')

for _ in range(SPARSEFLOWS + BULKFLOWS):
    queue().enter(passiveQueues)


for i in range(0,2*SPARSEFLOWS,2):
    sparseFlowGenerator(fid=i,interTime=time*INTERARRIVALMULTIPLIER, distribution="uniform")

for i in range(1,2*BULKFLOWS,2):
    bulkFlowGenerator(fid=i,interTime=time/20,distribution="uniform")




newQueues = sim.Queue('newQueues')
oldQueues = sim.Queue('oldQueues')


clerk = clerk(process=None)

env.run(till=RUNTIME)

print("interarrival time:", time*INTERARRIVALMULTIPLIER)

for x in range(len(passiveQueues)):
    if int(passiveQueues[x].packetCounter) == 0:
        print("Did not activate")
        continue
    print("Flow id:",passiveQueues[x].qid , "% sparse", passiveQueues[x].activateCounter/passiveQueues[x].packetCounter, passiveQueues[x].activateCounter, passiveQueues[x].packetCounter, "Time in queue per packet: ", passiveQueues[x].totalQueueDelay/passiveQueues[x].packetCounter)

for x in range(len(newQueues)):
    print("Flow id:",newQueues[x].qid , "% sparse", newQueues[x].activateCounter/newQueues[x].packetCounter, newQueues[x].activateCounter, newQueues[x].packetCounter, "Time in queue per packet: ", newQueues[x].totalQueueDelay/newQueues[x].packetCounter)

for x in range(len(oldQueues)):
    print("Flow id:",oldQueues[x].qid , "% sparse", oldQueues[x].activateCounter/oldQueues[x].packetCounter, oldQueues[x].activateCounter, oldQueues[x].packetCounter, "Time in queue per packet: ", oldQueues[x].totalQueueDelay/oldQueues[x].packetCounter)

newQueues.print_statistics()
oldQueues.print_statistics()
