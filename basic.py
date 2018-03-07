import salabim as sim

FLOWS = 2

class flowGenerator(sim.Component):
    def process(self,fid):
        while True:
            flow(name='flow-' + str(fid), fid=fid)
            yield self.hold(sim.Uniform(5,15).sample())


class flow(sim.Component):
    def setup(self, fid):
        self.fid = fid
        self.packetSize = 1500 * 8

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
        self.credits = 0
        self.new = True
        self.qid = -1

    def move(self, source, destination):
        self.leave(source)
        self.enter(destination)
    
    
    def push(self, component):
        component.enter(self.queue)


class scheduler(sim.Component):
    def process(self):
        old = False 
        counter = 0

        while True:
            if newQueues and not old:
                queue = newQueues[0].queue
                clerk.activate(queue=queue)
                yield self.passivate()
                newQueues[0].move(newQueues, oldQueues)
                 
            elif oldQueues:
                queue = oldQueues[0].queue
                 
                old = True
                counter += 1
                if queue:
                    clerk.activate(queue=queue)
                    yield self.passivate()
                    oldQueues[0].move(oldQueues, oldQueues)
                else:
                    oldQueues[0].move(oldQueues, passiveQueues)
            
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
