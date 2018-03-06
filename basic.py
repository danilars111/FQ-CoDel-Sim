import salabim as sim


class queue(sim.Component):
    def setup(self):
        self.queue = sim.Queue('queue')
        self.credits = 0
        self.new = True

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
                newQueues[0].move(newQueues, oldQueues)
            
            else:
                queue = oldQueues[0].queue
                
                old = True
                counter += 1
                
                if queue:
                    oldQueues[0].move(oldQueues, oldQueues)

                else:
                    oldQueues[0].move[oldQueues, passiveQueues]



            if counter is len(oldQueues):
                old = False
                counter = 0

            if oldQueues[0] or newQueues[0]:
                clerk.activate(queue=queue)

            yield self.passivate()


class clerk(sim.Component):
    def process(self, queue):
        while True:
            queue.pop()
            scheduler.activate()
            yield self.passivate()


env = sim.Environment(trace=True)


passiveQueues = sim.Queue('passiveQueues')

#for _ in range(5):
 #   queue().enter(passiveQueues)


newQueues = sim.Queue('newQueues')
oldQueues = sim.Queue('oldQueues')

for y in range(5):
    queue().enter(newQueues)

    for _ in range(5):
        box = sim.Component('box')
        box.enter(newQueues[y].queue) 

for y in range(5):
    queue().enter(oldQueues)

    for _ in range(5):
        box = sim.Component('box')
        box.enter(oldQueues[y].queue) 

scheduler = scheduler()
clerk = clerk(process=None)

env.run(till=100)
