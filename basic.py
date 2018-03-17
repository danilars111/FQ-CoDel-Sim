import salabim as sim
import random

UNCLAIMED = -1
BANDWIDTH = 100.0 * pow(10,6)
FLOWS = 1
MSS = 1500.0 * 8
QUANTUM = MSS + (14 * 8)
INTERARRIVAL = MSS/(2 * BANDWIDTH)



class flowGenerator(sim.Component):
    def process(self,fid):
        while True:
            flow(name='flow-' + str(fid), fid=fid, size = random.uniform(1/MSS,1))
            yield self.hold(sim.Exponential(1).sample())


class flow(sim.Component):
    def setup(self, fid, size):
        self.fid = fid
        self.packetSize = round(size * MSS,0) - (round(size * MSS,0) % 8)
        
    def process(self):
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
                
                if scheduler.ispassive():
                    scheduler.activate()
                yield self.cancel()
        
        for l in range(len(passiveQueues)):
            if passiveQueues[l].qid is UNCLAIMED:
                passiveQueues[l].push(self)
                passiveQueues[l].qid = self.fid
                passiveQueues[l].move(passiveQueues, newQueues)

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
        self.sparseCounter = 0

    def move(self, source, destination):
        self.leave(source)
        self.enter(destination)
    
    
    def push(self, component):
        component.enter(self.queue)

    def resetCredits(self):
        self.credits = QUANTUM

    def sparseIncrease(self):
        if self.qid is not UNCLAIMED:
            self.sparseCounter += 1

class scheduler(sim.Component):
    def setup(self):
        self.RRCounter = 0

    def process(self):
        old = False 
        counter = 0

        while True:
            if newQueues and not old:
                queue = newQueues[0].queue
                
                while newQueues[0].credits > 0 and queue:
                    print("Block size", newQueues[0].queue[0].packetSize/8)

                    newQueues[0].credits -= queue[0].packetSize
                    print("credits =",newQueues[0].credits/8, "fid:", newQueues[0].qid)
                    
                    clerk.activate(queue=queue, size=queue[0].packetSize)
                    yield self.passivate()
                
                if newQueues[0].credits <= 0:
                    newQueues[0].credits += QUANTUM
                    
                newQueues[0].move(newQueues, oldQueues)
                 
            elif oldQueues:
                queue = oldQueues[0].queue
                 
                old = True
                counter += 1
                if queue:
                    while oldQueues[0].credits > 0 and queue:
                        
                        print("Block size", oldQueues[0].queue[0].packetSize/8)
                        oldQueues[0].credits -= queue[0].packetSize
                        print("credits =",oldQueues[0].credits/8), "fid:", oldQueues[0].qid
                        clerk.activate(queue=queue, size=queue[0].packetSize)
                        yield self.passivate()
                        
                    if oldQueues[0].credits <= 0:
                        oldQueues[0].credits += QUANTUM
                    
                    oldQueues[0].move(oldQueues, oldQueues)
                else:
                    oldQueues[0].resetCredits()
                    oldQueues[0].move(oldQueues, passiveQueues)
                    old = False
                    counter = 0
                    self.RRCounter += 1
                    for i in range(len(passiveQueues)):
                        passiveQueues[i].sparseIncrease()

            
            elif not self.ispassive():
               yield self.passivate()

            
            if counter is len(oldQueues) and old:
                print("counter reset")
                old = False
                counter = 0
                self.RRCounter += 1
                for i in range(len(passiveQueues)):
                    passiveQueues[i].sparseIncrease()




class clerk(sim.Component):
    def process(self, queue, size):
        while True:
            queue.pop()
            yield self.hold(size/BANDWIDTH)
            scheduler.activate()
            yield self.cancel()


env = sim.Environment(trace=True)

scheduler = scheduler()

for i in range(FLOWS):
    flowGenerator(fid=i)

passiveQueues = sim.Queue('passiveQueues')

for _ in range(FLOWS):
    queue().enter(passiveQueues)


newQueues = sim.Queue('newQueues')
oldQueues = sim.Queue('oldQueues')


clerk = clerk(process=None)

env.run(till=100)

print("Scheduler RR", scheduler.RRCounter)

for x in range(len(passiveQueues)):
    print("Flow id:",passiveQueues[x].qid ,"Sparse counter:", passiveQueues[x].sparseCounter)

for x in range(len(newQueues)):
    print("Flow id:",newQueues[x].qid ,"Sparse counter:",newQueues[x].sparseCounter)

for x in range(len(oldQueues)):
    print("Flow id:",oldQueues[x].qid ,"Sparse counter:", oldQueues[x].sparseCounter)

