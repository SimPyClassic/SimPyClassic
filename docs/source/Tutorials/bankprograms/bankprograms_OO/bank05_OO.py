""" bank05_OO: The single Random Customer """
from SimPy.Simulation import Simulation, Process, hold
from random import expovariate, seed                     

## Model components ------------------------           

class Customer(Process):
    """ Customer arrives at a random time,
        looks around  and then leaves """
    
    def visit(self,timeInBank):       
        print self.sim.now(), self.name," Here I am"             
        yield hold,self,timeInBank
        print self.sim.now(), self.name," I must leave"          

## Experiment data -------------------------

maxTime = 100.0    # minutes 
timeInBank = 10.0  # minutes
tMeanArrival = 5.0 # minutes

## Experiment ------------------------------
seed(0)

sim = Simulation()
sim.initialize()
c = Customer(name="Klaus",sim=sim)
t = expovariate(1.0/tMeanArrival)
sim.activate(c,c.visit(timeInBank),at=t)               
sim.simulate(until=maxTime)
