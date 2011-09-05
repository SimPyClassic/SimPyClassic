""" bank05: The single Random Customer """
from SimPy.Simulation import *
from random import expovariate, seed                     

## Model components ------------------------           

class Customer(Process):
    """ Customer arrives at a random time,
        looks around  and then leaves """
    
    def visit(self,timeInBank):       
        print now(), self.name," Here I am"             
        yield hold,self,timeInBank
        print now(), self.name," I must leave"          

## Experiment data -------------------------

maxTime = 100.0    # minutes                                    
timeInBank = 10.0
## Model/Experiment ------------------------------

seed(99999)                                            
initialize()
c = Customer(name = "Klaus")
t = expovariate(1.0/5.0)                               
activate(c,c.visit(timeInBank),at=t)                 
simulate(until=maxTime)
