""" bank05_OO: The single Random Customer """
from SimPy.Simulation import *
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
timeInBank = 10.0
## Model -----------------------------------
class BankModel(Simulation):
   def run(self):
       self.initialize()
       c = Customer(name = "Klaus",sim=self)
       t = expovariate(1.0/5.0)
       self.activate(c,c.visit(timeInBank),at=t)               
       self.simulate(until=maxTime)
## Experiment ------------------------------
seed(99999) 
BankModel().run()