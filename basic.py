import salabim as sim
import random

UNCLAIMED = -1
BANDWIDTH = input("Enter bandwidth (Mbps): ") * pow(10,6)
SPARSEFLOWS = input("Enter number of sparseflows: ")
BULKFLOWS = input("Enter number of bulkflows: ")
MSS = 1500.0 * 8.0
QUANTUM = MSS + (14.0 * 8.0)
INTERARRIVALMULTIPLIER = input("Enter interarrivaltime multiplier ")
RUNTIME = input("Enter simulated runtime: ")
TRACE = input("Trace?: ")
old = False

def sparseCalc():
    return ((QUANTUM*(BULKFLOWS + 1)) + (SPARSEFLOWS*QUANTUM/2.0))/BANDWIDTH


class sparseFlowGenerator(sim.Component):
    def process(self,fid, interTime, distribution="uniform"):
       
        if distribution is "uniform":
            while True:
                flow(name='sflow-' + str(fid), fid=fid, size = QUANTUM/2.0)
                        #random.uniform(1,QUANTUM/8) * 8)
                yield self.hold(interTime)

        elif distribution is "exponential":
            while True:
                flow(name='sflow-' + str(fid), fid=fid, size = QUANTUM/2.0)
                    #random.uniform(1, QUANTUM/8) * 8)
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
    def process(self):
        #if self.fid is 0:
            #print("Incoming Packet with size:", self.packetSize)
        global old 
        
        for i in range(len(newQueues)):
            if newQueues[i].qid is self.fid:
                newQueues[i].push(self)
                yield self.cancel()

        for j in range(len(oldQueues)):
            if oldQueues[j].qid is self.fid:
                oldQueues[j].push(self)
                yield self.cancel()

        for k in range(len(passiveQueues)):
            if passiveQueues[k].qid is self.fid:
                passiveQueues[k].push(self)
                passiveQueues[k].move(passiveQueues, newQueues) 
                old = False
                #print("Flow old:", old)

                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()
        
        for l in range(len(passiveQueues)):
            if passiveQueues[l].qid is UNCLAIMED:
                passiveQueues[l].push(self)
                passiveQueues[l].qid = self.fid
                passiveQueues[l].move(passiveQueues, newQueues)

                old = False
                print("Flow old:", old)
                
                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()

        print("No available queues\n")
        yield self.cancel()


class queue(sim.Component):
    def setup(self):
        self.queue = sim.Queue()
        self.credits = QUANTUM
        self.new = True
        self.qid = UNCLAIMED
        self.sparseCounter = 0.0

    def move(self, source, destination):
        self.leave(source)
        self.enter(destination)
        #if self.qid is 0:
        #    print("Moving:", self.qid, "from", source, "to", destination, "length of queue", len(self.queue), "credits", self.credits)
    
    def push(self, component):
        component.enter(self.queue)

    def resetCredits(self):
        self.credits = QUANTUM

    def sparseIncrease(self):
        if self.qid is not UNCLAIMED:
            self.sparseCounter += 1
            #print("increasing sparse for:", self.qid)


class scheduler(sim.Component):
    def setup(self):
        self.RRCounter = 0.0

    def process(self):
        counter = 0
        global old
        old = False

        while True:
            
            if not old:
                if not newQueues:
                    old = True
                   # print("Scheduler old:",old)    
                else:
                    queue = newQueues[0].queue
                
                    while newQueues[0].credits > 0 and queue:
                        #if newQueues[0].qid is 0:
                            #print("Deducting", queue[0].packetSize, "credits")
                    # print("Block size", newQueues[0].queue[0].packetSize/8)

                        newQueues[0].credits -= queue[0].packetSize
                    #print("credits =",newQueues[0].credits/8, "fid:", newQueues[0].qid)
                    
                        clerk.activate(queue=queue, size=queue[0].packetSize)
                        yield self.passivate()
                
                    if newQueues[0].credits <= 0:
                        newQueues[0].credits += QUANTUM

                    #if newQueues[0].qid is 0:
                        #print("Adding Quantum")
                    
                    newQueues[0].move(newQueues, oldQueues)
                 
            elif oldQueues and old:
                queue = oldQueues[0].queue
                 
                counter += 1
                if queue:
                    while oldQueues[0].credits > 0 and queue:
                        #if oldQueues[0].qid is 0:
                            #print("Deducting", queue[0].packetSize, "credits")
                        
                       # print("Block size", oldQueues[0].queue[0].packetSize/8)
                        oldQueues[0].credits -= queue[0].packetSize
                       # print("credits =",oldQueues[0].credits/8), "fid:", oldQueues[0].qid
                        clerk.activate(queue=queue, size=queue[0].packetSize)
                        yield self.passivate()
                        
                    if oldQueues[0].credits <= 0:
                        oldQueues[0].credits += QUANTUM
                        #if oldQueues[0].qid is 0:
                            #print("Adding Quantum")
                    
                    oldQueues[0].move(oldQueues, oldQueues)
                else:
                    oldQueues[0].resetCredits()
                    oldQueues[0].move(oldQueues, passiveQueues)
                    counter = 0
                    #self.RRCounter += 1
                    
                    for i in range(len(passiveQueues)):
                        passiveQueues[i].sparseIncrease()
                
                    for i in range(len(newQueues)):
                        newQueues[i].sparseIncrease()
            

            elif not self.ispassive():
               yield self.passivate()

            
            if counter is len(oldQueues) and old:
               # print("RR reset")
                counter = 0
                self.RRCounter += 1
                
                for i in range(len(passiveQueues)):
                    passiveQueues[i].sparseIncrease()

                for i in range(len(newQueues)):
                    newQueues[i].sparseIncrease()



class clerk(sim.Component):
    def process(self, queue, size):
        while True:
            queue.pop()
            #print("before hold")
            scheduler.activate(delay=(size/BANDWIDTH),urgent=True)
            yield self.cancel()


env = sim.Environment(trace=TRACE,random_seed=None)


scheduler = scheduler()

time = sparseCalc()

passiveQueues = sim.Queue('passiveQueues')

for _ in range(SPARSEFLOWS + BULKFLOWS + 1):
    queue().enter(passiveQueues)


for i in range(0,2*SPARSEFLOWS,2):
    sparseFlowGenerator(fid=i,interTime=time*INTERARRIVALMULTIPLIER, distribution="uniform")

for i in range(1,2*BULKFLOWS,2):
    bulkFlowGenerator(fid=i,interTime=time/4,distribution="uniform")




newQueues = sim.Queue('newQueues')
oldQueues = sim.Queue('oldQueues')


clerk = clerk(process=None)

env.run(till=RUNTIME)

print("interarrival time:", time*INTERARRIVALMULTIPLIER)

print("Scheduler RR", scheduler.RRCounter)

for x in range(len(passiveQueues)):
    print("Flow id:",passiveQueues[x].qid , "% sparse",  passiveQueues[x].sparseCounter/scheduler.RRCounter)

for x in range(len(newQueues)):
    print("Flow id:",newQueues[x].qid ,"% sparse",  newQueues[x].sparseCounter/scheduler.RRCounter)

for x in range(len(oldQueues)):
    print("Flow id:",oldQueues[x].qid ,"% sparse",  oldQueues[x].sparseCounter/scheduler.RRCounter)

