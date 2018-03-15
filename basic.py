import salabim as sim
import random

FLOWS = 2
MSS = 1500 * 8
QUANTUM = MSS + (14 * 8)

class flowGenerator(sim.Component):
    def process(self,fid):
        while True:
            flow(name='flow-' + str(fid), fid=fid, size = random.uniform(1/MSS,1))
            yield self.hold(sim.Uniform(5,15).sample())


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

        passiveQueues[0].push(self)
        passiveQueues[0].qid = self.fid
        passiveQueues[0].move(passiveQueues, newQueues)

        if scheduler.ispassive():
            scheduler.activate()
        
        yield self.cancel()


class queue(sim.Component):
    def setup(self):
        self.queue = sim.Queue()
        self.credits = QUANTUM
        self.new = True
        self.qid = -1

    def move(self, source, destination):
        self.leave(source)
        self.enter(destination)
    
    
    def push(self, component):
        component.enter(self.queue)

    def resetCredits(self):
        self.credits = QUANTUM

class scheduler(sim.Component):
    def process(self):
        old = False 
        counter = 0

        while True:
            if newQueues and not old:
                queue = newQueues[0].queue
                
                while newQueues[0].credits > 0 and queue:
                    newQueues[0].credits -= queue[0].packetSize
                    print("credits =",newQueues[0].credits/8, "fid:", newQueues[0].qid)
                    clerk.activate(queue=queue)
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
                        oldQueues[0].credits -= queue[0].packetSize
                        print("credits =",oldQueues[0].credits/8), "fid:", oldQueues[0].qid
                        clerk.activate(queue=queue)
                        yield self.passivate()
                        
                    if oldQueues[0].credits <= 0:
                        oldQueues[0].credits += QUANTUM
                    
                    oldQueues[0].move(oldQueues, oldQueues)
                else:
                    oldQueues[0].resetCredits()
                    oldQueues[0].move(oldQueues, passiveQueues)
                    old = False
                    counter = 0
            
            elif not self.ispassive():
               yield self.passivate()

            print(old)
            if counter is len(oldQueues) and old:
                print("counter reset")
                old = False
                counter = 0




class clerk(sim.Component):
    def process(self, queue):
        while True:
            queue.pop()
            yield self.hold(10)
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
