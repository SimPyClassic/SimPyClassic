""" bank06: Many Random Customers """
from SimPy.Simulation import Simulation, Process, hold
from random import expovariate,seed            

## Model components ------------------------

class Source(Process):
    """ Source generates customers at random """

    def generate(self,number,meanTBA):       
        for i in range(number):
            c = Customer(name = "Customer%02d"%(i,),sim=self.sim)
            self.sim.activate(c,c.visit(timeInBank=12.0)) 
            t = expovariate(1.0/meanTBA)      
            yield hold,self,t                  

class Customer(Process):
    """ Customer arrives, looks round and leaves """
        
    def visit(self,timeInBank=0):       
        print "%7.4f %s: Here I am"%(self.sim.now(),self.name)
        yield hold,self,timeInBank
        print "%7.4f %s: I must leave"%(self.sim.now(),self.name)

## Model -----------------------------------

## Experiment data -------------------------

maxNumber = 5
maxTime = 400.0 # minutes                                   
ARRint = 10.0   # mean arrival interval, minutes 

## Experiment ------------------------------

# NOTE: Set a seed so that output is deterministic.
seed(0)

sim = Simulation()
sim.initialize()
s = Source(name='Source',sim=sim)
sim.activate(s,s.generate(number=maxNumber,
              meanTBA=ARRint),at=0.0)
sim.simulate(until=maxTime)
