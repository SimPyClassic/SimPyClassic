""" bank01_OO: The single non-random Customer """           
from SimPy.Simulation import *                           

## Model components -----------------------------        

class Customer(Process):                                 
    """ Customer arrives, looks around and leaves """
        
    def visit(self,timeInBank):                          
        print self.sim.now(),self.name," Here I am"               
        yield hold,self,timeInBank                       
        print self.sim.now(),self.name," I must leave"            

## Experiment data ------------------------------

maxTime = 100.0     # minutes                            
timeInBank = 10.0   # mean, minutes

## Model ----------------------------------------
class BankModel(Simulation):
    def run(self):
        self.initialize()                                             
        c = Customer(name="Klaus",sim=self)                               
        self.activate(c,c.visit(timeInBank),at=5.0)                   
        self.simulate(until=maxTime) 

## Experiment -----------------------------------
BankModel().run()