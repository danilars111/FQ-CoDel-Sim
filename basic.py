import salabim as sim

class queue(sim.Component):
    def process(self):
        self.queue = sim.Queue('queue')
        yield self.passivate()

class move(sim.Component):
    def process(self):
        self.queue = passiveQueues.pop()
        self.queue.enter(newQueues)
        yield self.passivate()

class addToQueue(sim.Component):
    def process(self):
        self.queue = newQueues[0]
        data.enter(self.queue.queue)
        yield self.passivate

class data(sim.Component):
    def nothing(self):
        self.hold(1)


env = sim.Environment(trace=True)

interArrivalTime = sim.Uniform(5,15).sample()

passiveQueues = sim.Queue('passiveQueues')

for _ in range(5):
    queue().enter(passiveQueues)

newQueues = sim.Queue('newQueues')
oldQueues = sim.Queue('newQueues')

move()
data = data()
addToQueue()

env.run(till=100)
