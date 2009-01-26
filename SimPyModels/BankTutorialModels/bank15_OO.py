"""bank15_OO: Monitoring a Resource"""
from SimPy.Simulation  import *
from random import *

## Model components ------------------------

class Source(Process):                                        
    """ Source generates customers randomly"""
    def generate(self,number,rate):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=12.0,counter=self.sim.counter))
            yield hold,self,expovariate(rate)

class Customer(Process):                                      
    """ Customer arrives, is served and leaves """
    def visit(self,timeInBank,counter):       
        arrive=now()
        print "%8.4f %s: Arrived     "%(self.sim.now(),self.name)

        yield request,self,counter
        print "%8.4f %s: Got counter "%(self.sim.now(),self.name)
        tib = expovariate(1.0/timeInBank)
        yield hold,self,tib
        yield release,self,counter

        print "%8.4f %s: Finished    "%(self.sim.now(),self.name)

## Experiment data -------------------------

maxTime = 400.0    # minutes                                               

## Model  ----------------------------------

class BankModel(Simulation):
    def run(self):
        self.initialize()
        self.counter = Resource(capacity=1,name="Clerk",monitored=True,sim=self) 
        source = Source(sim=self)                                                         
        self.activate(source,
                 source.generate(number=5,rate=0.1),at=0.0)    
        self.simulate(until=maxTime)

        return (self.counter.waitMon.timeAverage(),self.counter.actMon.timeAverage()) 

## Experiment  ----------------------------------

seed(393939)
print 'Average waiting = %6.4f\nAverage active  = %6.4f\n'%BankModel().run() 

